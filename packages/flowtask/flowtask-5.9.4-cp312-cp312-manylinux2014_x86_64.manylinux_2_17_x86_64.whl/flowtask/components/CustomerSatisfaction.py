from collections.abc import Callable
import asyncio
from ..interfaces.ParrotBot import ParrotBot
from .flow import FlowComponent


class CustomerSatisfaction(ParrotBot, FlowComponent):
    """
        CustomerSatisfaction

        Overview

            The CustomerSatisfaction class is a component for interacting with an IA Agent for making Customer Satisfaction Analysis.
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

    

        Example:

        ```yaml
        CustomerSatisfaction:
          llm:
            name: VertexLLM
            model_name: gemini-1.5-pro
            temperature: 0.4
          review_column: review
          product_column: product_name
          columns:
          - product_id
          - product_name
          - product_model
          - product_type
          - product_variant
          - account_name
          - picture_url
          - url
          output_column: customer_satisfaction
        ```

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
        self._goal: str = "Customer Satisfaction Analysis using Reviews"

    def format_question(self, product_name, reviews):
        question = f"""
        Product: {product_name}

        Question:
        "What is the overall customer sentiment, likes and dislikes,
        and what insights can be derived from these product reviews for product: {product_name}?"

        Customer Reviews:

        """
        for review in reviews:
            question += f"* {review}\n"
        return question

    async def run(self):
        self._result = await self.bot_evaluation()
        self._print_data_(self._result, 'CustomerSatisfaction')
        return self._result

    async def close(self):
        pass
