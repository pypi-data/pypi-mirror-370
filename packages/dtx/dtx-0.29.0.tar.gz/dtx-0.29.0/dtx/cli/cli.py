import sys

# from dtx.cli.check_dep import check_modules
from rich.console import Console

from pathlib import Path

# Check if torch is found in the env
# if check_modules(["torch", "transformers"], required_pkg="dtx[torch]"):
from .planner import PlanInput, RedTeamPlanGenerator

import argparse
from dotenv import load_dotenv
from rich.prompt import Prompt
from typing import List, Optional
from dtx_models.analysis import PromptDataset
from dtx_models.providers.base import ProviderType
from dtx_models.analysis import RedTeamPlan
from dtx_models.template.prompts.base import PromptsRepoType
from dtx_models.repo.plugin import PluginRepo
from dtx.plugins.providers.gradio.cli import GradioProviderGenerator
from dtx.plugins.providers.http.cli import HttpProviderBuilderCli
from dtx.plugins.prompts.langhub.cli import LangHubPromptGenerator
from .agents_builder_cli import InteractiveAgentBuilder

from .console_output import (
    RichDictPrinter,
    RichResultVisualizer,
)
from .providers import ProviderFactory
from .scoping import RedTeamScopeCreator, ScopeInput
from .env_manager import EnvLoader
from .evaluatorargs import EvalMethodArgs

from .datasetargs import DatasetArgs
from .validatorsargs import EnvValidator

from .format import SmartFormatter


# Load env
load_dotenv()

# Configure Env Variable

EnvLoader().load_env()
EnvLoader().configure()


class AgentScanner:
    """Command-line tool to create and manage agent scope YAML files."""

    def __init__(self):
        self.selected_evaluator = EvalMethodArgs()
        self.select_dataset = DatasetArgs()
        self.args = self._parse_arguments()

    # --- Argument parsing ---
    def _parse_arguments(self):
        parser = argparse.ArgumentParser(
            description="Agent Scanner CLI",
            formatter_class=lambda prog: SmartFormatter(
                prog, max_help_position=40, width=150
            ),
        )
        subparsers = parser.add_subparsers(
            dest="command", help="Available commands", required=True
        )

        # REDTEAM COMMANDS
        redteam_parser = subparsers.add_parser(
            "redteam",
            help="Red teaming operations",
            formatter_class=lambda prog: SmartFormatter(
                prog, max_help_position=40, width=150
            ),
        )
        redteam_parser.add_argument("--headless", action="store_true", help="Disable all output saving")
        redteam_subparsers = redteam_parser.add_subparsers(
            dest="redteam_command", required=True
        )

        ## Quick Red Teaming
        redteam_subparsers.add_parser(
            "quick",
            help="Assistant to create plan and initiate Redteam",
        )

        ## Create Red Team Scope
        scope_parser = redteam_subparsers.add_parser(
            "scope", help="Generate red team scope"
        )

        scope_parser.add_argument(
            "--plugin", dest="plugins", action="append", default=[],
            help="Plugin ID, keyword, or regex expression (use multiple times for more plugins)"
        )

        scope_parser.add_argument(
            "--framework", dest="frameworks", action="append", default=[],
            help="AI Framework name or pattern (use multiple times for more)"
        )

        scope_parser.add_argument("description", type=str, help="Scope description")
        scope_parser.add_argument(
            "output", type=str, nargs="?", default="redteam_scope.yml"
        )

        plan_parser = redteam_subparsers.add_parser(
            "plan",
            help="Generate red team plan",
            formatter_class=lambda prog: SmartFormatter(
                prog, max_help_position=40, width=150
            ),
        )
        plan_parser.add_argument("scope_file", type=str)
        plan_parser.add_argument(
            "output", type=str, nargs="?", default="redteam_plan.yml"
        )
        plan_parser.add_argument("--max_prompts", type=int, default=20)
        plan_parser.add_argument("--max_prompts_per_plugin", type=int, default=100)
        plan_parser.add_argument("--max_goals_per_plugin", type=int, default=10)

        self.select_dataset.augment_args(plan_parser)

        run_parser = redteam_subparsers.add_parser(
            "run",
            help="Run red team tests",
            formatter_class=lambda prog: SmartFormatter(
                prog, max_help_position=40, width=150
            ),
        )
        run_parser.add_argument(
            "--agent",
            type=str,
            choices=ProviderType.values() + PromptsRepoType.values(),
            help="Choose an AgentInfo (optional if plan provided)",
        )
        run_parser.add_argument(
            "--plugin", dest="plugins", action="append", default=[],
            help="Plugin ID, keyword, or regex expression (use multiple times for more plugins)"
        )

        run_parser.add_argument(
            "--framework", dest="frameworks", action="append", default=[],
            help="AI Framework name or pattern (use multiple times for more)"
        )

        run_parser.add_argument("--plan_file", type=str, help="Redteam plan file path")
        run_parser.add_argument("--url", type=str, default="", help="Agent Url / Model Name")
        run_parser.add_argument("--max_prompts", type=int, default=20)
        run_parser.add_argument("--tactics", type=str, action="append", default=[])
        run_parser.add_argument("--samples", type=int, default=1, help="Number of samples per prompt")
        run_parser.add_argument("--threads", type=int, default=1, help="Number of threads to use (currently must be 1)")
        run_parser.add_argument("--headless", action="store_true", help="Disable all output saving")

        run_parser.add_argument(
            "--yml", type=str, default="report.yml", help="output yml file path"
        )
        run_parser.add_argument(
            "--json", type=str, default="report.json", help="output json file path"
        )
        run_parser.add_argument(
            "--html", type=str, default="report.html", help="output html file path"
        )
        run_parser.add_argument(
            "-o", "--output", action="store_true", help="Enable saving output file"
        )
        run_parser.add_argument("--max_prompts_per_plugin", type=int, default=100)
        run_parser.add_argument("--max_goals_per_plugin", type=int, default=20)
        
        self.select_dataset.augment_args(run_parser)
        self.selected_evaluator.augment_args(run_parser)

        # PLUGINS
        plugins_parser = subparsers.add_parser("plugins", help="Manage plugins")
        plugins_subparsers = plugins_parser.add_subparsers(dest="plugins_command")
        plugins_subparsers.add_parser("list", help="List plugins")

        # PROVIDERS
        providers_parser = subparsers.add_parser("providers", help="Manage providers")
        providers_subparsers = providers_parser.add_subparsers(dest="providers_command")
        generate_parser = providers_subparsers.add_parser("generate")
        generate_parser.add_argument(
            "provider", type=ProviderType, choices=ProviderType.values()
        )
        generate_parser.add_argument("--url", type=str, default="")
        generate_parser.add_argument("--output", type=str, default="")

        # PROMPTS
        prompts_parser = subparsers.add_parser("prompts", help="Manage prompts")
        prompts_subparsers = prompts_parser.add_subparsers(dest="prompts_command")
        generate_prompts_parser = prompts_subparsers.add_parser(
            "generate", help="Generate prompts"
        )
        generate_prompts_parser.add_argument(
            "prompts_repo", type=PromptsRepoType, choices=PromptsRepoType.values()
        )
        generate_prompts_parser.add_argument(
            "--url", type=str, default="", help="URL for prompt repository provider"
        )
        generate_prompts_parser.add_argument(
            "--output", type=str, default="", help="Output file for prompts"
        )

        # DATASETS & TACTICS
        subparsers.add_parser("datasets").add_subparsers(
            dest="datasets_command"
        ).add_parser("list")
        subparsers.add_parser("tactics").add_subparsers(
            dest="tactics_command"
        ).add_parser("list")

        # ENV
        env_parser = subparsers.add_parser("env", help="Environment variable helpers")
        env_parser.add_subparsers(dest="env_command").add_parser(
            "list", help="List required environment variables"
        )

        return parser.parse_args()

    # --- Main entrypoint ---
    def run(self):
        match self.args.command:
            case "redteam":
                self._handle_redteam()
            case "providers":
                self._handle_providers()
            case "prompts":
                self._handle_prompts()
            case "datasets" if self.args.datasets_command == "list":
                self.list_datasets()
            case "plugins" if self.args.plugins_command == "list":
                self.list_plugins()
            case "tactics" if self.args.tactics_command == "list":
                self.list_tactics()
            case "env" if self.args.env_command == "list":
                self.list_env_dependencies()
            case _:
                print("Invalid command. Use --help for usage.")

    # --- REDTEAM Operations ---
    def _handle_redteam(self):

        if self.args.headless:
            from dtx.core import logging
            logging.set_level("error")
        try:
            EnvValidator.validate(
                dataset=getattr(self.args, "dataset", None),
                eval_name=getattr(self.args, "eval", None),
            )
        except EnvironmentError as e:
            print(str(e))
            sys.exit(1)

        match self.args.redteam_command:
            case "scope":
                self._generate_scope(self.args.description, self.args.output, plugins=self.args.plugins)
            case "plan":
                self._generate_plan(
                    scope_file=self.args.scope_file,
                    output=self.args.output,
                    max_prompts=self.args.max_prompts,
                    max_prompts_per_plugin=self.args.max_prompts_per_plugin,
                    max_goals_per_plugin=self.args.max_goals_per_plugin
                )
            case "run":
                self._run_tests()
            case "quick":
                self._redteam_interactive_quick()
            case _:
                print("Invalid redteam subcommand")

    def _run_tests(self):

        from .runner import QuickRedteamRunner, QuickRedteamRunnerInput


        collector = RichResultVisualizer(headless=self.args.headless)

        if self.args.plan_file:
            input_data = QuickRedteamRunnerInput(
                plan_file=self.args.plan_file,
                max_prompts=self.args.max_prompts,
                max_prompts_per_plugin=self.args.max_prompts_per_plugin,
                max_goals_per_plugin=self.args.max_goals_per_plugin,
                agent=self.args.agent,
                url=self.args.url,
                output=self.args.output,
                yml_file=self.args.yml,
                json_file=self.args.json,
                collector=collector,
                html_file=self.args.html
            )
        else:
            # Validate argument combinations before running
            self._validate_args_combinations()

            dataset = self.select_dataset.parse_args(self.args)
            global_eval = self.selected_evaluator.parse_args(self.args)

            input_data = QuickRedteamRunnerInput(
                plan_file=self.args.plan_file,
                max_prompts=self.args.max_prompts,
                max_prompts_per_plugin=self.args.max_prompts_per_plugin,
                max_goals_per_plugin=self.args.max_goals_per_plugin,
                samples_per_prompt=self.args.samples,
                threads=self.args.threads,
                agent=self.args.agent,
                url=self.args.url,
                output=self.args.output,
                yml_file=self.args.yml,
                json_file=self.args.json,
                html_file=self.args.html,
                dataset=dataset,
                evaluator=global_eval,
                tactics=[],
                plugins=self.args.plugins,
                frameworks=self.args.frameworks,
                collector=collector,
            )
            input_data.set_tactics_by_name(names=self.args.tactics)

        runner = QuickRedteamRunner(input_data)
        runner.run()

    def _resolve_agent_and_url(self, plan: RedTeamPlan):
        if self.args.agent:
            return self.args.agent, self.args.url

        return self._resolve_agent_and_url_from_plan(plan=plan)

    def _resolve_agent_and_url_from_plan(self, plan: RedTeamPlan):
        if plan.scope.providers:
            provider = plan.scope.providers[0]
            agent_type = provider.provider
            url = getattr(provider.config, "model", getattr(provider.config, "url", ""))
            print(f"🧩 Using provider from plan: agent={agent_type}, url={url}")
            return agent_type, url

        raise ValueError(
            "No agent specified. Use --agent or provide a plan file with provider information."
        )

    def _create_scope(self, description=None):
        description = description or "It is a default scope"
        scope_config = ScopeInput(
            description=description,
            plugins=self.args.plugins,
            frameworks=self.args.frameworks
        )
        creator = RedTeamScopeCreator(config=scope_config)
        scope = creator.run()

        global_eval = self.selected_evaluator.parse_args(self.args)
        if global_eval:
            scope.redteam.global_evaluator = global_eval
        return scope

    def _run_tests_initialize_agent(self, plan, agent_type, url):
        return ProviderFactory(load_env_vars=True).get_agent(plan.scope, agent_type, url)

    def _run_tests_initialize_collector(self, headless=False):
        return RichResultVisualizer(headless=headless)

    def _generate_scope(self, description, output, plugins: Optional[List[str]]=None):
        config = ScopeInput(description=description, plugins=plugins, frameworks=self.args.frameworks)
        creator = RedTeamScopeCreator(config=config)
        creator.run()
        creator.save_yaml(output)


    def _generate_plan(self, scope_file, output, 
                    max_prompts, 
                    max_prompts_per_plugin, 
                    max_goals_per_plugin=5):
        scope = RedTeamScopeCreator.load_yaml(scope_file)
        dataset = self.select_dataset.parse_args(self.args)
        scope.redteam.max_prompts = max_prompts
        scope.redteam.max_prompts_per_plugin = max_prompts_per_plugin
        scope.redteam.max_goals_per_plugin = max_goals_per_plugin

        config = PlanInput(
            dataset=dataset
        )
        generator = RedTeamPlanGenerator(scope=scope, config=config)
        generator.run()
        generator.save_yaml(output)

    def _redteam_interactive_quick(self):

        from .runner import QuickRedteamRunner, QuickRedteamRunnerInput

        console = Console()
        builder = InteractiveAgentBuilder(console=console)
        plan = builder.run()

        if not plan:
            console.print("[red]❌ Plan creation failed or was cancelled.[/red]")
            return

        # Step 1: Save YAML files (scope + plan)
        plan_file = builder.save_yaml(plan=plan)

        # Step 2: Ask user if they want to run the tests now
        run_now = Prompt.ask(
            "[bold cyan]Do you want to run the RedTeam tests now?[/bold cyan] (yes/no)",
            choices=["yes", "no"],
            default="yes",
        )

        if run_now.lower() != "yes":
            console.print("[yellow]⚠️ Skipping RedTeam test execution.[/yellow]")
            return

        # Step 3: Ask user for output report file
        output_file = Prompt.ask(
            "Enter the filename to save the RedTeam test results",
            default="report.yml",
        )
        output_json = Path(output_file).with_suffix(".json").as_posix()
        output_html = Path(output_file).with_suffix(".html").as_posix()

        # Step 4: Resolve agent info and prepare runner input
        agent_type, url = self._resolve_agent_and_url_from_plan(plan)
        agent = self._run_tests_initialize_agent(plan, agent_type, url)
        collector = self._run_tests_initialize_collector(headless=self.args.headless)

        input_data = QuickRedteamRunnerInput(
            plan_file=plan_file,
            agent=agent_type,
            url=url,
            max_prompts=1000,
            tactics=[],
            output=True,
            yml_file=output_file,
            json_file=output_json,
            html_file=output_html,
            collector=collector
        )

        # Step 5: Run the tests using QuickRedteamRunner
        console.print("[bold green]🚀 Running RedTeam tests...[/bold green]")
        runner = QuickRedteamRunner(input_data)
        runner.run()

        # Step 6: Confirm save location
        console.print(f"RedTeam test results saved to [green]{output_file}[/green]")


    # --- Utilities ---
    def list_env_dependencies(self):
        deps = EnvValidator.list_all_dependencies()
        all_rows = {}

        for dataset, envs in deps["datasets"].items():
            deps_list = self._format_env_dependency(envs)
            if deps_list != "-":
                all_rows[f"Dataset: {dataset}"] = deps_list

        for eval_name, envs in deps["evals"].items():
            deps_list = ", ".join(envs) if envs else "-"
            if deps_list != "-":
                all_rows[f"Eval: {eval_name}"] = deps_list

        if not all_rows:
            print("🎉 No environment dependencies found!")
            return

        printer = RichDictPrinter("Environment Dependencies", "Item", "Dependencies")
        printer.print(all_rows)

    @staticmethod
    def _format_env_dependency(env_map):
        parts = []
        if env_map.get("all"):
            parts.append("All: " + ", ".join(env_map["all"]))
        if env_map.get("any"):
            parts.append("Any: " + ", ".join(env_map["any"]))
        return " | ".join(parts) if parts else "-"

    def _validate_args_combinations(self):

        global_eval = self.selected_evaluator.parse_args(self.args)
        dataset = self.select_dataset.parse_args(self.args)
        dataset_input = getattr(self.args, "dataset", None)

        if dataset in [PromptDataset.STINGRAY] and global_eval:
            if not self.args.eval:
                print(
                    f"❌ Error: It seems '{dataset_input}' dataset, and agent are not compatible."
                )
                sys.exit(1)
            else:
                print(
                    f"❌ Error: When using '{dataset_input}' dataset, you must not specify an evaluator with --eval."
                )
                sys.exit(1)

    # --- Providers and Prompts ---
    def _handle_providers(self):
        if self.args.providers_command == "generate":
            if self.args.provider == ProviderType.GRADIO:
                generator = GradioProviderGenerator(gradio_url=self.args.url)
                providers = generator.run()
                if providers:
                    generator.save_yaml(providers)
            elif self.args.provider == ProviderType.HTTP:
                builder = HttpProviderBuilderCli(url=self.args.url)
                provider_output = builder.run()
                builder.dump_yaml(provider_output, filename=self.args.output)
            else:
                print("Unsupported provider type for generation.")
        else:
            print("Invalid providers command")

    def _handle_prompts(self):
        if self.args.prompts_command == "generate":
            if self.args.prompts_repo == PromptsRepoType.LANGHUB:
                generator = LangHubPromptGenerator()
                providers = generator.run()
                if providers:
                    generator.save_yaml(providers)
            else:
                print("Unsupported prompts repository type for generation.")
        else:
            print("Invalid prompts command")

    def list_datasets(self):
        printer = RichDictPrinter("Available Prompt Datasets", "Dataset", "Description")
        printer.print(PromptDataset.descriptions())

    def list_plugins(self):
        plugin_map = PluginRepo.get_plugin_descriptions()
        printer = RichDictPrinter("Available Plugins", "Plugin", "Description")
        printer.print(plugin_map)

    def list_tactics(self):
        from dtx.config import globals
        tactics_repo = globals.get_tactics_repo(only=True)
        plugin_map = tactics_repo.get_tactics()
        printer = RichDictPrinter("Available Tactics", "Tactic", "Description")
        printer.print(plugin_map)


def main():
    scanner = AgentScanner()
    scanner.run()
