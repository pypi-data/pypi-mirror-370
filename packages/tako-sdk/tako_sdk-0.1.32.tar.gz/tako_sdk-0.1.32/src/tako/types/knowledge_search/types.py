from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

####
# This file contains the types for the knowledge search API
####


class KnowledgeSearchSourceIndex(str, Enum):
    TAKO = "tako"
    WEB = "web"


class KnowledgeSearchInputs(BaseModel):
    text: Optional[str] = Field(
        description="Natural language search query string. This can be a direct knowledge query, "
        "or long form text, for which relevant knowledge cards should be returned.",
        examples=[
            "AMD vs. Nvidia headcount since 2013",
            "What is the population of the United States?",
        ],
    )


class KnowledgeCardSource(BaseModel):
    source_name: Optional[str] = Field(
        description="The name of the source",
        examples=["S&P Global", "The World Bank"],
    )
    source_description: Optional[str] = Field(
        description="The description of the source",
        examples=[
            "S&P Global is a US-based financial data and analytics company that provides "
            "products and services to the financial industry.",
            "The World Bank is an international financial institution that provides "
            "financial and technical assistance to developing countries to help them "
            "achieve sustainable economic growth and improve living conditions.",
        ],
    )
    source_index: KnowledgeSearchSourceIndex = Field(
        description="The index of the source",
        examples=[KnowledgeSearchSourceIndex.TAKO, KnowledgeSearchSourceIndex.WEB],
    )
    url: Optional[str] = Field(
        description="The URL of the source",
        examples=["https://xignite.com", "https://stats.com"],
    )

    def __hash__(self) -> int:
        return hash(
            (self.source_name, self.source_description, self.source_index, self.url)
        )


class KnowledgeCardMethodology(BaseModel):
    methodology_name: Optional[str] = Field(
        description="The name of the methodology",
        examples=["Change me"],  # TODO
    )
    methodology_description: Optional[str] = Field(
        description="The description of the methodology",
        examples=["Change me"],  # TODO
    )

    def __hash__(self) -> int:
        return hash((self.methodology_name, self.methodology_description))


class KnowledgeCard(BaseModel):
    card_id: Optional[str] = Field(
        description="The unique ID of the knowledge card",
        examples=["08OoYXQeAjCs_8ybek96"],
    )
    title: Optional[str] = Field(
        description="The title of the knowledge card",
        examples=["Nvidia, Advanced Micro Devices - Full Time Employees"],
    )
    description: Optional[str] = Field(
        description="The description of the knowledge card",
        examples=[
            "This is a time series bar chart showing 2 series between 12:00AM UTC-04:00 on "
            "04/01/2013 and 08:55PM UTC on 04/30/2025. Nvidia Full Time Employees latest "
            "value was at 12:00AM UTC on 12-31-2024, and had a final value of 36.0K "
            "Employees, or 308.72% growth since 12:00AM UTC on 12-31-2013, with a maximum "
            "value of 36.0K Employees at 12:00AM UTC on 12-31-2024 and a minimum value of "
            "8.81K Employees at 12:00AM UTC on 12-31-2013; Advanced Micro Devices Full Time "
            "Employees latest value was at 12:00AM UTC on 12-31-2024, and had a final value "
            "of 28.0K Employees, or 162.39% growth since 12:00AM UTC on 12-31-2013, with a "
            "maximum value of 28.0K Employees at 12:00AM UTC on 12-31-2024 and a minimum "
            "value of 8.2K Employees at 12:00AM UTC on 12-31-2016. The source of the data "
            "is S&P Global. S&P Global is a US-based financial data and analytics company "
            "that provides products and services to the financial industry.",
        ],
    )
    webpage_url: Optional[str] = Field(
        description="URL of a webpage hosting the interactive knowledge card",
        examples=["https://trytako.com/card/08OoYXQeAjCs_8ybek96/"],
    )
    image_url: Optional[str] = Field(
        description="URL of a static image of the knowledge card",
        examples=["https://trytako.com/api/v1/image/08OoYXQeAjCs_8ybek96/"],
    )
    embed_url: Optional[str] = Field(
        description="URL of an embeddable iframe of the knowledge card",
        examples=["https://trytako.com/embed/08OoYXQeAjCs_8ybek96/"],
    )
    sources: Optional[List[KnowledgeCardSource]] = Field(
        description="The sources of the knowledge card",
    )
    methodologies: Optional[List[KnowledgeCardMethodology]] = Field(
        description="The methodologies of the knowledge card",
    )
    source_indexes: Optional[List[KnowledgeSearchSourceIndex]] = Field(
        description="The source indexes of the knowledge card",
    )
    card_type: Optional[str] = Field(
        description="The type of card",
        examples=["company", "chart", "table", "text"],
    )


class KnowledgeSearchOutputs(BaseModel):
    knowledge_cards: Optional[List[KnowledgeCard]] = None


class KnowledgeSearchResults(BaseModel):
    outputs: Optional[KnowledgeSearchOutputs] = None
    request_id: Optional[str] = None


class KnowledgeCardOutputSettings(BaseModel):
    image_dark_mode: Optional[bool] = Field(
        description="Whether to make the knowledge card image dark mode",
        default=False,
    )


class KnowledgeSearchRequestOutputSettings(BaseModel):
    knowledge_card_settings: KnowledgeCardOutputSettings = Field(
        description="Settings for the knowledge card outputs",
    )

class KnowledgeSearchRequest(BaseModel):
    inputs: KnowledgeSearchInputs = Field(
        description="The inputs for the knowledge search request"
    )

    # Priority order of potential source indexes to search
    # Once relevant results are found in a source index, the search will stop
    # and results from remaining source indexes will not be searched
    source_indexes: Optional[List[KnowledgeSearchSourceIndex]] = Field(
        description="The priority order of potential source indexes to search."
        "Once relevant results are found in a source index, the search will stop"
        "and results from remaining source indexes will not be searched."
        "Valid values are: tako, web",
        default=[KnowledgeSearchSourceIndex.TAKO],
    )

    output_settings: Optional[KnowledgeSearchRequestOutputSettings] = Field(
        description="Settings for controlling outputs of the knowledge search request",
        default=None,
    )

    country_code: str = Field(
        description="ISO3166-1 alpha-2 country code (e.g., 'US', 'CA', 'GB')",
        default="US",  # greatest country in the world
    )
