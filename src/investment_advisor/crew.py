from typing import Any, List

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

from .tools.market_data_tool import MarketDataTool
from .tools.news_sentiment_tool import NewsSentimentTool
from .tools.risk_analyzer_tool import RiskAnalyzerTool


load_dotenv()


@CrewBase
class InvestmentAdvisorCrew:
    """AI Investment Advisor crew orchestrating specialized financial agents."""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # === Agents ===
    def _base_agent(self, config_key: str, tools: List[Any] | None = None) -> Agent:
        return Agent(
            config=self.agents_config[config_key],
            verbose=True,
            tools=tools or [],
        )

    @agent
    def market_data_agent(self) -> Agent:
        return self._base_agent('market_data_agent', tools=[MarketDataTool()])

    @agent
    def news_sentiment_agent(self) -> Agent:
        return self._base_agent('news_sentiment_agent', tools=[NewsSentimentTool()])

    @agent
    def risk_analyzer_agent(self) -> Agent:
        return self._base_agent('risk_analyzer_agent', tools=[RiskAnalyzerTool()])

    @agent
    def recommendation_agent(self) -> Agent:
        return self._base_agent('recommendation_agent')

    # === Tasks ===
    def _task(self, key: str, agent: Agent, context: List[Task] | None = None) -> Task:
        return Task(
            config=self.tasks_config[key],
            agent=agent,
            context=context or [],
        )

    @task
    def market_data_task(self) -> Task:
        return self._task('market_data_task', self.market_data_agent())

    @task
    def news_sentiment_task(self) -> Task:
        return self._task(
            'news_sentiment_task',
            self.news_sentiment_agent(),
            context=[self.market_data_task()],
        )

    @task
    def risk_analysis_task(self) -> Task:
        return self._task(
            'risk_analysis_task',
            self.risk_analyzer_agent(),
            context=[self.market_data_task(), self.news_sentiment_task()],
        )

    @task
    def recommendation_task(self) -> Task:
        return self._task(
            'recommendation_task',
            self.recommendation_agent(),
            context=[
                self.market_data_task(),
                self.news_sentiment_task(),
                self.risk_analysis_task(),
            ],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the AI Investment Advisor workflow."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
