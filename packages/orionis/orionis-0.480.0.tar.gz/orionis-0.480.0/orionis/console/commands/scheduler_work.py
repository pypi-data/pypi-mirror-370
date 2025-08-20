import importlib.util
import os
from pathlib import Path
from orionis.console.base.command import BaseCommand
from orionis.console.contracts.schedule import ISchedule
from orionis.console.exceptions import CLIOrionisRuntimeError
from orionis.foundation.contracts.application import IApplication
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from datetime import datetime

class ScheduleWorkCommand(BaseCommand):
    """
    Command class to display usage information for the Orionis CLI.
    """

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "schedule:work"

    # Command description
    description: str = "Executes the scheduled tasks defined in the application."

    async def handle(self, orionis: IApplication, console: Console) -> bool:

        try:

            # Obtener la ruta absoluta del scheduler desde la configuración de la aplicación
            scheduler_path = orionis.path('console_scheduler')

            # Obtener la base path desde la variable de entorno o desde la configuración local
            base_path = Path(os.getcwd()).resolve()
            scheduler_path = Path(scheduler_path).resolve()
            rel_path = scheduler_path.relative_to(base_path)

            # Reemplazar los separadores por puntos y quitar la extensión .py
            module_name = ".".join(rel_path.with_suffix('').parts)

            # Importar el módulo del scheduler
            scheduler_module = importlib.import_module(module_name)

            # Obtener la clase Scheduler del módulo importado
            Scheduler = getattr(scheduler_module, "Scheduler", None)

            # Check if the Scheduler class was found
            if Scheduler is None:
                raise CLIOrionisRuntimeError(f"Scheduler class not found in module {module_name}")

            # Obtener el método tasks de la clase Scheduler
            task_method = getattr(Scheduler, "tasks", None)

            # Check if the method exists
            if task_method is None:
                raise CLIOrionisRuntimeError(f"Method 'tasks' not found in Scheduler class in module {module_name}")

            # Crear una instancia de ISchedule
            schedule_serice: ISchedule = orionis.make(ISchedule)

            # Inicializar el metodo
            task_method(schedule_serice)

            # Display a professional start message for the scheduler worker
            console.line()
            start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            panel_content = Text.assemble(
                (" Orionis Scheduler Worker ", "bold white on green"),
                ("\n\n", ""),
                ("The scheduled tasks worker has started successfully.\n", "white"),
                (f"Started at: {start_time}\n", "dim"),
                ("To stop the worker, press ", "white"),
                ("Ctrl+C", "bold yellow"),
                (".", "white")
            )
            console.print(
                Panel(panel_content, border_style="green", padding=(1, 2))
            )
            console.line()

            # Iniciar el scheduler
            await schedule_serice.start()

        except Exception as exc:

            # Catch any unexpected exceptions and raise as a CLIOrionisRuntimeError
            raise CLIOrionisRuntimeError(f"An unexpected error occurred while clearing the cache: {exc}")
