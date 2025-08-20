"""
Manages background tasks.
"""
from asyncio import Task, CancelledError, Queue, create_task, gather
from collections.abc import Coroutine
from typing import Any, Callable, Optional
from aiohttp import web
import logging

class BackgroundTasks:
    """
    Manages asyncio background tasks. An instance of this class is available as an application property with name
    HEA_BACKGROUND_TASKS.
    """
    def __init__(self, app: web.Application | None = None, queue_size= 0):
        """
        Creates a background task manager with the provided queue size.

        :param queue_size: the queue size. A value of zero means infinite size.
        """
        self.__app = app
        self.__tasks: dict[str, Task] = dict()
        self.__done: dict[str, Exception | None] = dict()
        self.__queue = Queue[Task](queue_size)
        self.__metadata: dict[str, dict[str, Any]] = dict()
        self.__result: dict[str, Any] = dict()
        self.__logger = logging.getLogger(__name__)

    def contains(self, name: str) -> bool:
        """
        Whether this background task manager is managing a task with the given name.

        :param name: the name of the background task.
        :return True or False.
        """
        return name in self.__tasks or name in self.__done

    async def add(self, coro: Callable[[Optional[web.Application]], Coroutine[Any, Any, None]], name: str | None = None, **metadata) -> str:
        """
        A coroutine for creating a new asyncio task from the given coroutine and adds it to the tasks managed by this
        task manager. If a name is provided, the task will be given the provided name. Otherwise, a name will be
        generated automatically.

        :param coro: the coroutine (required).
        :param name: an optional name.
        :param metadata: any key-value pairs associated with the task.
        :return: the name of the created task.
        """
        self.__logger.debug('Adding coroutine %s...', name)
        task = create_task(coro(self.__app), name=name)
        name_ = task.get_name()
        self.__tasks[name_] = task
        self.__metadata[name_] = metadata
        await self.__queue.put(task)
        self.__logger.debug('Coroutine %s added.', name_)
        return name_

    def metadata(self, name: str, key: str) -> Any:
        """
        Retrieve task metadata.

        :param name: the name of the task.
        :param key: the key of the metadata value of interest.
        :return: the metadata value.
        :raises KeyError: if the given task has no metadata with the given key.
        """
        return self.__metadata[name][key]

    def cancel(self, name: str):
        """
        Requests cancellation of the task with the given name.

        :param name: the name of the task to cancel.
        """
        self.__tasks[name].cancel()

    def cancel_all(self):
        """
        Requests cancellation of all tasks managed by this background task manager.
        """
        for task in self.__tasks.values():
            task.cancel()

    async def join(self, name: str):
        """
        A coroutine for awaiting completion of the task with the given name.

        :param name: the name of the task.
        """
        try:
            await self.__tasks[name]
        except:
            pass
        finally:
            self._mark_done(name)

    async def join_all(self) -> None:
        """
        A coroutine for awaiting completion of all tasks managed by this backround task manager.
        """
        done_tasks: list[str] = []
        for name, task in self.__tasks.items():
            try:
                await task
            except:
                pass
            finally:
                done_tasks.append(name)
        for name in done_tasks:
            self._mark_done(name)

    def in_progress(self, name: str) -> bool:
        """
        Returns whether the task is managed by this task manager and is still running.

        :param name: the name of the task.
        :return: True or False.
        """
        return self.contains(name) and not self.done(name)

    def done(self, name: str) -> bool:
        """
        Returns whether the task with the given name is completed.

        :param name: the name of the task to check.
        :return: True or False.
        """
        return name in self.__done

    def succeeded(self, name: str) -> bool:
        """
        Returns whether the task with the given name completed successfully.

        :param name: the name of the task to check.
        :return: True or False.
        """
        return bool(self.done(name) and not self.error(name))

    def failed(self, name: str) -> bool:
        """
        Returns whether the task with the given name failed.

        :param name: the name of the task to check.
        :return: True or False.
        """
        return bool(self.done(name) and self.error(name))

    def error(self, name: str) -> Exception | None:
        """
        Returns the exception raised within a failed task.

        :param name: the name of the task to check.
        :return: An exception if the task failed, or None if it succeeded.
        :raises ValueError: if the task is not done or not managed by this background task manager.
        """
        if name not in self.__done:
            raise ValueError(f'{name} not done or not managed by this background task manager.')
        return self.__done[name]

    def result(self, name: str) -> Any:
        if name not in self.__done:
            raise ValueError(f'{name} not done or not managed by this background task manager.')
        return self.__result[name]

    def remove(self, name: str):
        """
        Removes the task with the given name from this task manager. This method does nothing if no task with the given
        name is managed by this background task manager.

        :param name: the name of the task to remove.
        """
        if name in self.__tasks:
            del self.__tasks[name]
        if name in self.__done:
            del self.__done[name]
        if name in self.__metadata:
            del self.__metadata[name]

    async def clear(self):
        """
        A coroutine that cancels all running tasks and cleans up all resources.
        """
        self.cancel_all()
        await self.join_all()
        while not self.__queue.empty():
            self.__queue.get_nowait()
            self.__queue.task_done()
        self.__tasks.clear()
        self.__done.clear()
        self.__metadata.clear()

    async def auto_join(self):
        """
        A coroutine that automatically executes tasks added to this task manager. It runs forever. When wrapped in a
        task, cancelling the task ends this coroutine.
        """
        async def consumer():
            while task := await self.__queue.get():
                try:
                    await self.join(task.get_name())
                    self.__queue.task_done()
                except CancelledError:
                    await self.join(task.get_name())
                    self.__queue.task_done()
                    raise


        consumers = [create_task(consumer()) for _ in range(5)]
        try:
            await gather(*consumers)
        except CancelledError:
            for c in consumers:
                c.cancel()
            raise



    def __len__(self) -> int:
        """
        Returns the number of tasks managed by this background task manager.

        :return: the number of tasks managed by this background task manager.
        """
        return len(self.__tasks) + len(self.__done)

    def running_tasks(self) -> int:
        """
        Returns the number of running tasks.

        :return: the number of running tasks.
        """
        return len(self.__tasks)

    def done_tasks(self) -> int:
        """
        Returns the number of done tasks.

        :return: the number of done tasks.
        """
        return len(self.__done)

    def _mark_done(self, name: str):
        """
        Marks the task with the given name as done.

        :param name: the name of the task to mark done.
        """
        try:
            self.__result[name] = self.__tasks[name].result()
            self.__done[name] = None
        except CancelledError:
            self.__done[name] = None
            self.__result[name] = None
        except Exception as e:
            self.__done[name] = e
        self.__tasks.pop(name, None)

    def __str__(self) -> str:
        return f'Background task manager: in-progress tasks: {", ".join(self.__tasks)}; done tasks: {", ".join(self.__done)}'
