from collections.abc import Callable
import asyncio
from ..interfaces.ParrotBot import ParrotBot
from .flow import FlowComponent


class ProductCompliant(ParrotBot, FlowComponent):
    """
        ProductCompliant

        Overview

            The ProductCompliant class is a component for interacting with an IA Agent for making Customer Satisfaction Analysis.
            It extends the FlowComponent class.

        .. table:: Properties
        :widths: auto

            +------------------+----------+--------------------------------------------------------------------------------------------------+
            | Name             | Required | Description                                                                                      |
            +------------------+----------+--------------------------------------------------------------------------------------------------+
            | output_column    |   Yes    | Column for saving the Customer Satisfaction information.                                         |
            +------------------+----------+--------------------------------------------------------------------------------------------------+
        Return

            A Pandas Dataframe with the Customer Satisfaction statistics.

    """ # noqa

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        super().__init__(
            loop=loop, job=job, stat=stat, **kwargs
        )
        self._goal: str = 'Your task is to provide a concise and insightful analysis on negative reviews of products'

    def format_question(self, product_name, reviews):
        question = f"""
            Product: {product_name}

            Question:
            "What are the primary customer concerns, problems, and issues based on these negative product reviews for {product_name}?"

            Negative Customer Reviews:

        """
        for review in reviews:
            question += f"* {review}\n"
        return question

    async def run(self):
        self._result = await self.bot_evaluation()
        self._print_data_(self._result, 'ProductCompliant')
        return self._result

    async def close(self):
        pass
