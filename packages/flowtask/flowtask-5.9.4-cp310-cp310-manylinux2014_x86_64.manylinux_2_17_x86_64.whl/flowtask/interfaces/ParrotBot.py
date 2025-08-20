from abc import abstractmethod
from typing import Any
from navconfig.logging import logging
from parrot.bots.basic import BasicBot
from ..exceptions import ConfigError, ComponentError

class ParrotBot:
    """ParrotBot.

    Interface for creating new chatbots to be used directly as Flowtask Components

    """
    def __init__(self, *args, **kwargs):
        self._bot_name = kwargs.get('bot_name', 'ParrotBot')
        self._bot: Any = None
        self._logger = logging.getLogger(f'Bot.{self._bot_name.lower()}')
        self._prompt_file = kwargs.get('prompt_file', 'prompt.txt')
        self._goal: str = kwargs.get('goal', 'Customer Satisfaction Analysis using Reviews')
        self._rating_column: str = kwargs.get('rating_column', 'rating')
        self._eval_column: str = kwargs.get('eval_column', 'evaluation')
        self._desc_column: str = kwargs.get('description_column', 'description')
        self.output_column: str = kwargs.get('output_column')
        # System Prompt:
        self.system_prompt = "Customer Satisfaction: "
        super(ParrotBot, self).__init__(*args, **kwargs)
        # TaskStorage
        # Find in the taskstorage, the "prompts" directory.
        prompt_path = self._taskstore.path.joinpath(self._program, 'prompts')
        if not prompt_path.exists():
            raise ConfigError(
                f"{self.system_prompt} Prompts Path Not Found: {prompt_path}"
            )
        self.prompt_path = prompt_path
        # is hardcoded to this particular Bot.
        self.system_prompt_file = self._prompt_file
        # Bot Object:
        self._bot: Any = None

    async def start(self, **kwargs):
        """
            start

            Overview

                The start method is a method for starting the CustomerSatisfaction component.

            Parameters

                kwargs: dict
                    A dictionary containing the parameters for the CustomerSatisfaction component.

            Return

                True if the CustomerSatisfaction component started successfully.

        """
        if self.previous:
            self.data = self.input
        else:
            raise ComponentError(
                f"{self._bot_name.lower()}: Data Was Not Found"
            )
        if not self.output_column:
            raise ConfigError(
                f"{self._bot_name.lower()}: output_column is required"
            )
        # check if Prompt File exists
        prompt_file = self.prompt_path.joinpath(self.system_prompt_file)
        if not prompt_file.exists():
            raise ConfigError(
                f"{self.system_prompt} Prompt File Not Found: {prompt_file}"
            )
        self.system_prompt_file = prompt_file.name
        # read the prompt file as text:
        with open(prompt_file, 'r') as f:
            self.system_prompt = f.read()
        # Set the Bot:
        try:
            self._bot = BasicBot(
                name=self._bot_name,
                system_prompt=self.system_prompt,
                goal=self._goal,
                use_llm=self.llm.get('name', 'name'),
                model_name=self.llm.get('model_name', 'gemini-2.0-pro'),
            )
            # configure the bot:
            await self._bot.configure()
        except Exception as err:
            raise ComponentError(
                f"{self.system_prompt} Error Configuring Bot: {err}"
            ) from err
        return True

    @abstractmethod
    def format_question(self, obj_name, reviews):
        pass

    async def bot_evaluation(self):
        """
            bot_evaluation

            Overview

                The run method is a method for running the ParrotBot component.

            Return

                A Pandas Dataframe with the IA-based statistics.

        """
        # Group reviews by product_name and aggregate them into a list
        grouped = self.data.groupby(self._desc_column)[self._eval_column].apply(list).reset_index()
        _evaluation = {}
        for _, row in grouped.iterrows():
            product_name = row[self._desc_column]
            reviews = row[self._eval_column]
            formatted_question = self.format_question(product_name, reviews)
            result = await self._bot.question(
                question=formatted_question,
                return_docs=False
            )
            _evaluation[product_name] = {
                "answer": result.answer
            }
        # Then, create a dataframe only with the columns in "self.columns" grouped.
        grouped_df = self.data.groupby(self.columns).agg(
            num_reviews=(self._eval_column, "count"),
            avg_rating=(self._rating_column, "mean")
        ).reset_index()
        # Add the Customer Satisfaction column, using the dictionary and match per product_name column
        grouped_df[self.output_column] = grouped_df[self._desc_column].map(
            lambda x: _evaluation[x]['answer']
        )
        # Remove the starting ```json and ending ``` using a regex
        grouped_df[self.output_column] = grouped_df[self.output_column].str.replace(r'^```json\s*|\s*```$', '', regex=True)
        # return the grouped dataframe
        return grouped_df
