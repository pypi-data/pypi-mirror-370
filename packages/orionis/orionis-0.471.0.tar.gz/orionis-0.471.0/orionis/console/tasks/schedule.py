from typing import Any, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler as APSBackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler as APSBlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler as APSAsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from orionis.console.contracts.reactor import IReactor
from datetime import datetime
import pytz
import asyncio
from typing import Union
from orionis.console.exceptions import CLIOrionisRuntimeError
from orionis.app import Orionis

class Scheduler():

    def __init__(
        self,
        reactor: IReactor
    ) -> None:
        """
        Initialize a new instance of the Scheduler class.

        This constructor sets up the internal state required for scheduling commands,
        including references to the application instance, APScheduler schedulers, the
        command reactor, and job tracking structures. It also initializes properties
        for managing the current scheduling context.

        Parameters
        ----------
        reactor : IReactor
            An instance of a class implementing the IReactor interface, used to
            retrieve available commands and execute scheduled jobs.

        Returns
        -------
        None
            This method does not return any value. It initializes the Scheduler instance.
        """

        # Store the application instance for configuration access.
        self.__app = Orionis()

        # Initialize scheduler instances (will be set up later).
        self.__background_scheduler: APSBackgroundScheduler = None
        self.__blocking_scheduler: APSBlockingScheduler = None
        self.__asyncio_scheduler: APSAsyncIOScheduler = None
        self.__initScheduler()

        # Store the reactor instance for command management.
        self.__reactor = reactor

        # Retrieve and store all available commands from the reactor.
        self.__available_commands = self.__getCommands()

        # Dictionary to hold all scheduled jobs and their details.
        self.__jobs: dict = {}

        # Properties to track the current scheduling context.
        self.__command: str = None      # The command signature to be scheduled.
        self.__args: List[str] = None   # Arguments for the command.
        self.__purpose: str = None      # Purpose or description of the scheduled job.
        self.__type: str = None         # Scheduler type (background, blocking, asyncio).

    def __initScheduler(
        self
    ) -> None:
        """
        Initialize the internal APScheduler instances for background, blocking, and asyncio scheduling.

        This method creates and configures three types of schedulers:
        - BackgroundScheduler: Runs jobs in the background using threads.
        - BlockingScheduler: Runs jobs in the foreground and blocks the main thread.
        - AsyncIOScheduler: Integrates with asyncio event loops for asynchronous job execution.

        The timezone for all schedulers is set based on the application's configuration.

        Returns
        -------
        None
            This method does not return any value. It initializes internal scheduler attributes.
        """

        # Initialize the BackgroundScheduler with the application's timezone
        self.__background_scheduler = APSBackgroundScheduler(
            timezone=pytz.timezone(self.__app.config('app.timezone', 'UTC'))
        )

        # Initialize the BlockingScheduler with the application's timezone
        self.__blocking_scheduler = APSBlockingScheduler(
            timezone=pytz.timezone(self.__app.config('app.timezone', 'UTC'))
        )

        # Initialize the AsyncIOScheduler with the application's timezone
        self.__asyncio_scheduler = APSAsyncIOScheduler(
            timezone=pytz.timezone(self.__app.config('app.timezone', 'UTC'))
        )

    def __getCommands(
        self
    ) -> dict:
        """
        Retrieve available commands from the reactor and return them as a dictionary.

        This method queries the reactor for all available jobs/commands, extracting their
        signatures and descriptions. The result is a dictionary where each key is the command
        signature and the value is another dictionary containing the command's signature and
        its description.

        Returns
        -------
        dict
            A dictionary mapping command signatures to their details. Each value is a dictionary
            with 'signature' and 'description' keys.
        """

        # Initialize the commands dictionary
        commands = {}

        # Iterate over all jobs provided by the reactor's info method
        for job in self.__reactor.info():

            # Store each job's signature and description in the commands dictionary
            commands[job['signature']] = {
                'signature': job['signature'],
                'description': job.get('description', '')
            }

        # Return the commands dictionary
        return commands

    def background(
        self
    ) -> 'Scheduler':
        """
        Set the scheduler type to 'background' for job scheduling.

        This method configures the scheduler to use the BackgroundScheduler, which runs jobs in the background using threads.
        It updates the internal type property to indicate that subsequent scheduled jobs should be handled by the background scheduler.

        Returns
        -------
        Scheduler
            Returns the current instance of the Scheduler to allow method chaining.
        """

        # Set the scheduler type to 'background'
        self.__type = 'background'

        # Return self to support method chaining
        return self

    def blocking(
        self
    ) -> 'Scheduler':
        """
        Set the scheduler type to 'blocking' for job scheduling.

        This method configures the scheduler to use the BlockingScheduler, which runs jobs in the foreground and blocks the main thread.
        It updates the internal type property so that subsequent scheduled jobs will be handled by the blocking scheduler.

        Returns
        -------
        Scheduler
            Returns the current instance of the Scheduler to allow method chaining.
        """

        # Set the scheduler type to 'blocking'
        self.__type = 'blocking'

        # Return self to support method chaining
        return self

    def asyncio(
        self
    ) -> 'Scheduler':
        """
        Set the scheduler type to 'asyncio' for job scheduling.

        This method configures the scheduler to use the AsyncIOScheduler, which integrates with
        asyncio event loops for asynchronous job execution. It updates the internal type property
        so that subsequent scheduled jobs will be handled by the asyncio scheduler.

        Returns
        -------
        Scheduler
            Returns the current instance of the Scheduler to allow method chaining.
        """

        # Set the scheduler type to 'asyncio'
        self.__type = 'asyncio'

        # Return self to support method chaining
        return self

    def __isAvailable(
        self,
        signature: str
    ) -> bool:
        """
        Check if a command with the given signature is available.

        This method iterates through the available commands and determines
        whether the provided signature matches any registered command.

        Parameters
        ----------
        signature : str
            The signature of the command to check for availability.

        Returns
        -------
        bool
            True if the command with the specified signature exists and is available,
            False otherwise.
        """

        # Iterate through all available command signatures
        for command in self.__available_commands.keys():

            # Return True if the signature matches an available command
            if command == signature:
                return True

        # Return False if the signature is not found among available commands
        return False

    def __getDescription(
        self,
        signature: str
    ) -> Optional[str]:
        """
        Retrieve the description of a command given its signature.

        This method looks up the available commands dictionary and returns the description
        associated with the provided command signature. If the signature does not exist,
        it returns None.

        Parameters
        ----------
        signature : str
            The unique signature identifying the command.

        Returns
        -------
        Optional[str]
            The description of the command if found; otherwise, None.
        """

        # Attempt to retrieve the command entry from the available commands dictionary
        command_entry = self.__available_commands.get(signature)

        # Return the description if the command exists, otherwise return None
        return command_entry['description'] if command_entry else None

    def __getScheduler(
        self
    ) -> Optional[Union[APSBackgroundScheduler, APSBlockingScheduler, APSAsyncIOScheduler]]:
        """
        Retrieve the appropriate APScheduler instance based on the current scheduler type.

        This method selects and returns the internal scheduler instance corresponding to the
        type specified by the user (background, blocking, or asyncio). The scheduler type is
        determined by the value of the internal `__type` attribute, which is set using the
        `background()`, `blocking()`, or `asyncio()` methods.

        Returns
        -------
        Optional[Union[APSBackgroundScheduler, APSBlockingScheduler, APSAsyncIOScheduler]]
            The scheduler instance matching the current type, or None if the type is not set
            or does not match any known scheduler.
        """

        # Return the BackgroundScheduler if the type is set to 'background'
        if self.__type == 'background':
            return self.__background_scheduler

        # Return the BlockingScheduler if the type is set to 'blocking'
        elif self.__type == 'blocking':
            return self.__blocking_scheduler

        # Return the AsyncIOScheduler if the type is set to 'asyncio'
        elif self.__type == 'asyncio':
            return self.__asyncio_scheduler

    def __reset(
        self
    ) -> None:
        """
        Reset the internal state of the Scheduler instance.

        This method clears the current command, arguments, purpose, type, trigger,
        start time, and end time attributes, effectively resetting the scheduler's
        configuration to its initial state. This can be useful for preparing the
        scheduler for a new command or job scheduling without retaining any previous
        settings.

        Returns
        -------
        None
            This method does not return any value. It modifies the internal state of the Scheduler.
        """

        self.__command = None
        self.__args = None
        self.__purpose = None
        self.__type = None

    def command(
        self,
        signature: str,
        args: Optional[List[str]] = None
    ) -> 'Scheduler':
        """
        Register a command to be scheduled with the specified signature and optional arguments.

        This method validates the provided command signature and arguments, checks if the command
        is available in the list of registered commands, and stores the command details internally
        for scheduling. The command's description is also retrieved and stored for reference.

        Parameters
        ----------
        signature : str
            The unique signature identifying the command to be scheduled. Must be a non-empty string.
        args : Optional[List[str]], optional
            A list of string arguments to be passed to the command. If not provided, an empty list is used.

        Returns
        -------
        Scheduler
            Returns the current instance of the Scheduler to allow method chaining.

        Raises
        ------
        ValueError
            If the signature is not a non-empty string, if the arguments are not a list or None,
            or if the command signature is not available among registered commands.
        """

        # Validate that the command signature is a non-empty string
        if not isinstance(signature, str) or not signature.strip():
            raise ValueError("Command signature must be a non-empty string.")

        # Ensure that arguments are either a list of strings or None
        if args is not None and not isinstance(args, list):
            raise ValueError("Arguments must be a list of strings or None.")

        # Check if the command is available in the registered commands
        if not self.__isAvailable(signature):
            raise ValueError(f"The command '{signature}' is not available or does not exist.")

        # Store the command signature
        self.__command = signature

        # If purpose is not already set, retrieve and set the command's description
        if self.__purpose is None:
            self.__purpose = self.__getDescription(signature)

        # Store the provided arguments or default to an empty list
        self.__args = args if args is not None else []

        # Return self to support method chaining
        return self

    def purpose(
        self,
        purpose: str
    ) -> 'Scheduler':
        """
        Set the purpose or description for the scheduled command.

        This method assigns a human-readable purpose or description to the command
        that is being scheduled. The purpose must be a non-empty string. This can
        be useful for documentation, logging, or displaying information about the
        scheduled job.

        Parameters
        ----------
        purpose : str
            The purpose or description to associate with the scheduled command.
            Must be a non-empty string.

        Returns
        -------
        Scheduler
            Returns the current instance of the Scheduler to allow method chaining.

        Raises
        ------
        ValueError
            If the provided purpose is not a non-empty string.
        """

        # Validate that the purpose is a non-empty string
        if not isinstance(purpose, str) or not purpose.strip():
            raise ValueError("The purpose must be a non-empty string.")

        # Set the internal purpose attribute
        self.__purpose = purpose

        # Return self to support method chaining
        return self

    def onceAt(
        self,
        date: datetime
    ) -> bool:
        """
        Schedule a command to run once at a specific date and time.

        This method schedules the currently registered command to execute exactly once at the
        specified datetime. If no scheduler type has been set, it defaults to using the background
        scheduler. The job is registered internally and added to the appropriate APScheduler instance.

        Parameters
        ----------
        date : datetime.datetime
            The date and time at which the command should be executed. Must be a valid `datetime` instance.

        Returns
        -------
        bool
            Returns True if the job was successfully scheduled.

        Raises
        ------
        CLIOrionisRuntimeError
            If the provided date is not a `datetime` instance, if the scheduler type is not defined,
            or if there is an error while scheduling the job.
        """

        try:

            # Ensure the provided date is a valid datetime instance.
            if not isinstance(date, datetime):
                raise CLIOrionisRuntimeError(
                    "The date must be an instance of datetime."
                )

            # If no scheduler type is set, default to background scheduler.
            if self.__type is None:
                self.background()

            # Register the job details internally.
            self.__jobs[self.__command] = {
                'signature': self.__command,
                'args': self.__args,
                'purpose': self.__purpose,
                'type': self.__type,
                'trigger': 'once_at',
                'start_at': date.strftime('%Y-%m-%d %H:%M:%S'),
                'end_at': date.strftime('%Y-%m-%d %H:%M:%S')
            }

            # Retrieve the appropriate scheduler instance.
            scheduler = self.__getScheduler()

            # Raise an error if the scheduler is not defined.
            if scheduler is None:
                raise CLIOrionisRuntimeError("No scheduler type has been defined.")

            # Add the job to the scheduler.
            scheduler.add_job(
                func= lambda command=self.__command, args=list(self.__args): self.__reactor.call(
                    command,
                    args
                ),
                trigger=DateTrigger(
                    run_date=date
                ),
                id=self.__command,
                name=self.__command,
                replace_existing=True
            )

            # Reset the internal state for future scheduling.
            self.__reset()

            # Return True to indicate successful scheduling.
            return True

        except Exception as e:

            # Reraise known CLIOrionisRuntimeError exceptions.
            if isinstance(e, CLIOrionisRuntimeError):
                raise e

            # Wrap and raise any other exceptions as CLIOrionisRuntimeError.
            raise CLIOrionisRuntimeError(f"Error scheduling the job: {str(e)}")

    def start(self) -> None:
        """
        Start all internal APScheduler instances (AsyncIO, Background, and Blocking).

        This method initiates the three scheduler types managed by this Scheduler instance:
        - AsyncIOScheduler: Integrates with asyncio event loops for asynchronous job execution.
        - BackgroundScheduler: Runs jobs in the background using threads.
        - BlockingScheduler: Runs jobs in the foreground and blocks the main thread.

        Each scheduler is started, allowing scheduled jobs to be executed according to their triggers.

        Returns
        -------
        None
            This method does not return any value. It starts all configured schedulers.
        """

        # Start the AsyncIOScheduler to handle asynchronous jobs.
        # Only start if there's an event loop running or we can create one
        try:
            asyncio.get_running_loop()
            self.__asyncio_scheduler.start()
        except RuntimeError:
            # No event loop is running, AsyncIOScheduler won't be started
            # This is normal for non-asyncio environments
            pass

        # Start the BackgroundScheduler to handle background jobs.
        self.__background_scheduler.start()

        # Start the BlockingScheduler to handle blocking jobs.
        self.__blocking_scheduler.start()

    def shutdown(self, wait=True) -> None:
        """
        Shut down all internal APScheduler instances (AsyncIO, Background, and Blocking).

        This method gracefully stops the three scheduler types managed by this Scheduler instance:
        - AsyncIOScheduler: Handles asynchronous job execution.
        - BackgroundScheduler: Runs jobs in the background using threads.
        - BlockingScheduler: Runs jobs in the foreground and blocks the main thread.

        Parameters
        ----------
        wait : bool, optional
            If True, the method will wait until all currently executing jobs are completed before shutting down the schedulers.
            If False, the schedulers will be shut down immediately without waiting for running jobs to finish. Default is True.

        Returns
        -------
        None
            This method does not return any value. It shuts down all configured schedulers.
        """

        # Validate that the wait parameter is a boolean.
        if not isinstance(wait, bool):
            raise ValueError("The 'wait' parameter must be a boolean value.")

        # Shut down the AsyncIOScheduler, waiting for jobs if specified.
        try:
            if self.__asyncio_scheduler.running:
                self.__asyncio_scheduler.shutdown(wait=wait)
        except Exception:
            # AsyncIOScheduler may not be running or may have issues in shutdown
            pass

        # Shut down the BackgroundScheduler, waiting for jobs if specified.
        if self.__background_scheduler.running:
            self.__background_scheduler.shutdown(wait=wait)

        # Shut down the BlockingScheduler, waiting for jobs if specified.
        if self.__blocking_scheduler.running:
            self.__blocking_scheduler.shutdown(wait=wait)

    def remove(self, signature:str) -> None:
        """
        Remove a scheduled job from all internal APScheduler instances.

        This method attempts to remove a job with the specified job ID from each of the
        managed schedulers: AsyncIOScheduler, BackgroundScheduler, and BlockingScheduler.
        If the job does not exist in a particular scheduler, that scheduler will ignore
        the removal request without raising an error.

        Parameters
        ----------
        signature : str
            The unique identifier of the job to be removed from the schedulers.

        Returns
        -------
        None
            This method does not return any value. It removes the job from all schedulers if present.
        """

        # Validate that the job signature is a non-empty string.
        if not isinstance(signature, str) or not signature.strip():
            raise ValueError("Job signature must be a non-empty string.")

        # Remove the job from the AsyncIOScheduler, if it exists.
        try:
            self.__asyncio_scheduler.remove_job(signature)
        except Exception:
            # Job may not exist in this scheduler, continue with others
            pass

        # Remove the job from the BackgroundScheduler, if it exists.
        try:
            self.__background_scheduler.remove_job(signature)
        except Exception:
            # Job may not exist in this scheduler, continue with others
            pass

        # Remove the job from the BlockingScheduler, if it exists.
        try:
            self.__blocking_scheduler.remove_job(signature)
        except Exception:
            # Job may not exist in this scheduler, ignore
            pass

    def jobs(self) -> dict:
        """
        Retrieve all scheduled jobs currently managed by the Scheduler.

        This method returns a dictionary containing information about all jobs that have been
        registered and scheduled through this Scheduler instance. Each entry in the dictionary
        represents a scheduled job, where the key is the command signature and the value is a
        dictionary with details such as the signature, arguments, purpose, type, trigger, start time,
        and end time.

        Returns
        -------
        dict
            A dictionary mapping command signatures to their corresponding job details. Each value
            is a dictionary containing information about the scheduled job.
        """

        # Return the internal dictionary holding all scheduled jobs and their details.
        return self.__jobs

    def start_asyncio_scheduler(self) -> bool:
        """
        Start the AsyncIOScheduler specifically.

        This method attempts to start only the AsyncIOScheduler. It's useful when you need
        to start the asyncio scheduler separately or when working in an asyncio environment.

        Returns
        -------
        bool
            True if the AsyncIOScheduler was started successfully, False otherwise.
        """

        try:
            # Check if we're in an asyncio environment
            asyncio.get_running_loop()
            if not self.__asyncio_scheduler.running:
                self.__asyncio_scheduler.start()
            return True
        except RuntimeError:
            # No event loop is running
            return False
        except Exception:
            # Other errors
            return False

    async def start_asyncio_scheduler_async(self) -> bool:
        """
        Start the AsyncIOScheduler in an async context.

        This method is designed to be called from async functions and ensures
        the AsyncIOScheduler is properly started within an asyncio event loop.

        Returns
        -------
        bool
            True if the AsyncIOScheduler was started successfully, False otherwise.
        """

        try:
            if not self.__asyncio_scheduler.running:
                self.__asyncio_scheduler.start()
            return True
        except Exception:
            return False

    def is_asyncio_scheduler_running(self) -> bool:
        """
        Check if the AsyncIOScheduler is currently running.

        Returns
        -------
        bool
            True if the AsyncIOScheduler is running, False otherwise.
        """

        return self.__asyncio_scheduler.running if self.__asyncio_scheduler else False

    def get_scheduler_status(self) -> dict:
        """
        Get the status of all schedulers.

        Returns
        -------
        dict
            A dictionary with the running status of each scheduler type.
        """

        return {
            'asyncio': self.__asyncio_scheduler.running if self.__asyncio_scheduler else False,
            'background': self.__background_scheduler.running if self.__background_scheduler else False,
            'blocking': self.__blocking_scheduler.running if self.__blocking_scheduler else False
        }