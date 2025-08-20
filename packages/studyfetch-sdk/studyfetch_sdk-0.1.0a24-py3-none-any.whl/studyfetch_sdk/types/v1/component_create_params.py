# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ..._utils import PropertyInfo

__all__ = [
    "ComponentCreateParams",
    "Config",
    "ConfigChatConfigDto",
    "ConfigChatConfigDtoGuardrailRule",
    "ConfigDataAnalystConfigDto",
    "ConfigFlashcardsConfigDto",
    "ConfigScenariosConfigDto",
    "ConfigScenariosConfigDtoCharacter",
    "ConfigScenariosConfigDtoTool",
    "ConfigPracticeTestConfigDto",
    "ConfigPracticeTestConfigDtoQuestionDistribution",
    "ConfigAudioRecapConfigDto",
    "ConfigExplainersConfigDto",
    "ConfigUploadsConfigDto",
    "ConfigTutorMeConfigDto",
    "ConfigChatAnalyticsConfigDto",
]


class ComponentCreateParams(TypedDict, total=False):
    config: Required[Config]
    """Component-specific configuration"""

    name: Required[str]
    """Name of the component"""

    type: Required[
        Literal[
            "chat",
            "data_analyst",
            "flashcards",
            "scenarios",
            "practice_test",
            "audio_recap",
            "tutor_me",
            "explainers",
            "uploads",
            "chat_analytics",
        ]
    ]
    """Type of component to create"""

    description: str
    """Component description"""

    metadata: object
    """Additional metadata"""


class ConfigChatConfigDtoGuardrailRule(TypedDict, total=False):
    id: Required[str]
    """Unique identifier for the rule"""

    action: Required[Literal["block", "warn", "modify"]]
    """Action to take when rule is triggered"""

    condition: Required[str]
    """Condition to check"""

    description: Required[str]
    """Description of the rule"""

    message: str
    """Message to show when rule is triggered"""


class ConfigChatConfigDto(TypedDict, total=False):
    model: Required[str]
    """AI model to use"""

    enable_component_creation: Annotated[bool, PropertyInfo(alias="enableComponentCreation")]
    """Enable component creation"""

    enable_follow_ups: Annotated[bool, PropertyInfo(alias="enableFollowUps")]
    """Enable follow-up questions"""

    enable_guardrails: Annotated[bool, PropertyInfo(alias="enableGuardrails")]
    """Enable guardrails for content moderation"""

    enable_history: Annotated[bool, PropertyInfo(alias="enableHistory")]
    """Enable conversation history"""

    enable_rag_search: Annotated[bool, PropertyInfo(alias="enableRAGSearch")]
    """Enable RAG search"""

    enable_voice: Annotated[bool, PropertyInfo(alias="enableVoice")]
    """Enable voice interactions"""

    enable_web_search: Annotated[bool, PropertyInfo(alias="enableWebSearch")]
    """Enable web search"""

    folders: List[str]
    """Folder IDs"""

    guardrail_rules: Annotated[Iterable[ConfigChatConfigDtoGuardrailRule], PropertyInfo(alias="guardrailRules")]
    """Guardrail rules for content moderation"""

    materials: List[str]
    """Material IDs"""

    max_steps: Annotated[float, PropertyInfo(alias="maxSteps")]
    """Maximum steps for multi-step tool calls"""

    max_tokens: Annotated[float, PropertyInfo(alias="maxTokens")]
    """Maximum tokens for response"""

    system_prompt: Annotated[str, PropertyInfo(alias="systemPrompt")]
    """System prompt for the chat"""

    temperature: float
    """Temperature for response generation"""


class ConfigDataAnalystConfigDto(TypedDict, total=False):
    model: Required[str]
    """AI model to use"""

    enable_component_creation: Annotated[bool, PropertyInfo(alias="enableComponentCreation")]
    """Enable component creation"""

    enable_follow_ups: Annotated[bool, PropertyInfo(alias="enableFollowUps")]
    """Enable follow-up questions"""

    enable_history: Annotated[bool, PropertyInfo(alias="enableHistory")]
    """Enable conversation history"""

    enable_rag_search: Annotated[bool, PropertyInfo(alias="enableRAGSearch")]
    """Enable RAG search"""

    enable_voice: Annotated[bool, PropertyInfo(alias="enableVoice")]
    """Enable voice interactions"""

    enable_web_search: Annotated[bool, PropertyInfo(alias="enableWebSearch")]
    """Enable web search"""

    folders: List[str]
    """Folder IDs"""

    group_ids: Annotated[List[str], PropertyInfo(alias="groupIds")]
    """Group IDs to filter data"""

    materials: List[str]
    """Material IDs"""

    max_steps: Annotated[float, PropertyInfo(alias="maxSteps")]
    """Maximum steps for multi-step tool calls"""

    max_tokens: Annotated[float, PropertyInfo(alias="maxTokens")]
    """Maximum tokens for response"""

    system_prompt: Annotated[str, PropertyInfo(alias="systemPrompt")]
    """System prompt for the data analyst"""

    temperature: float
    """Temperature for response generation"""


class ConfigFlashcardsConfigDto(TypedDict, total=False):
    card_types: Annotated[List[str], PropertyInfo(alias="cardTypes")]
    """Types of flashcards"""

    difficulty: Literal["easy", "medium", "hard", "mixed"]
    """Difficulty level"""

    folders: List[str]
    """Folder IDs"""

    learning_steps: Annotated[str, PropertyInfo(alias="learningSteps")]
    """Learning steps configuration"""

    materials: List[str]
    """Material IDs"""

    max_review_interval: Annotated[float, PropertyInfo(alias="maxReviewInterval")]
    """Maximum review interval in days"""

    model: str
    """AI model to use for flashcard generation"""

    total_flashcards: Annotated[float, PropertyInfo(alias="totalFlashcards")]
    """Total number of flashcards to generate"""

    view_mode: Annotated[Literal["spaced_repetition", "normal"], PropertyInfo(alias="viewMode")]
    """View mode for flashcards"""


class ConfigScenariosConfigDtoCharacter(TypedDict, total=False):
    id: Required[str]
    """Character ID"""

    name: Required[str]
    """Character name"""

    role: Required[str]
    """Character role"""

    description: str
    """Character description"""


class ConfigScenariosConfigDtoTool(TypedDict, total=False):
    id: Required[str]
    """Tool ID"""

    name: Required[str]
    """Tool name"""

    data_format: Annotated[str, PropertyInfo(alias="dataFormat")]
    """Data format provided by the tool"""

    description: str
    """Tool description"""

    type: str
    """Tool type"""


class ConfigScenariosConfigDto(TypedDict, total=False):
    characters: Iterable[ConfigScenariosConfigDtoCharacter]
    """Scenario characters"""

    context: str
    """Scenario context"""

    enable_history: Annotated[bool, PropertyInfo(alias="enableHistory")]
    """Enable history"""

    enable_voice: Annotated[bool, PropertyInfo(alias="enableVoice")]
    """Enable voice"""

    final_answer_prompt: Annotated[str, PropertyInfo(alias="finalAnswerPrompt")]
    """Final answer prompt"""

    folders: List[str]
    """Folder IDs"""

    format: str
    """Scenario format"""

    goal: str
    """Scenario goal"""

    greeting_character_id: Annotated[str, PropertyInfo(alias="greetingCharacterId")]
    """Character ID for greeting"""

    greeting_message: Annotated[str, PropertyInfo(alias="greetingMessage")]
    """Greeting message"""

    materials: List[str]
    """Material IDs"""

    model: str
    """AI model to use for scenario generation"""

    placeholder_text: Annotated[str, PropertyInfo(alias="placeholderText")]
    """Placeholder text"""

    requires_final_answer: Annotated[bool, PropertyInfo(alias="requiresFinalAnswer")]
    """Requires final answer"""

    tools: Iterable[ConfigScenariosConfigDtoTool]
    """Available tools"""


class ConfigPracticeTestConfigDtoQuestionDistribution(TypedDict, total=False):
    fillinblank: float
    """Number of fill in the blank questions"""

    frq: float
    """Number of free response questions"""

    multiplechoice: float
    """Number of multiple choice questions"""

    shortanswer: float
    """Number of short answer questions"""

    truefalse: float
    """Number of true/false questions"""


class ConfigPracticeTestConfigDto(TypedDict, total=False):
    question_types: Required[Annotated[List[str], PropertyInfo(alias="questionTypes")]]
    """Question types"""

    ai_generation_mode: Annotated[
        Literal["balanced", "comprehensive", "focused", "adaptive"], PropertyInfo(alias="aiGenerationMode")
    ]
    """AI generation mode"""

    allow_retakes: Annotated[bool, PropertyInfo(alias="allowRetakes")]
    """Allow retakes"""

    difficulty: Literal["easy", "medium", "hard", "mixed"]
    """Difficulty level"""

    folders: List[str]
    """Folder IDs"""

    materials: List[str]
    """Material IDs"""

    max_attempts: Annotated[float, PropertyInfo(alias="maxAttempts")]
    """Maximum attempts allowed"""

    model: str
    """AI model to use for question generation and grading"""

    passing_score: Annotated[float, PropertyInfo(alias="passingScore")]
    """Passing score percentage"""

    question_distribution: Annotated[
        ConfigPracticeTestConfigDtoQuestionDistribution, PropertyInfo(alias="questionDistribution")
    ]
    """Distribution of question types"""

    questions_per_test: Annotated[float, PropertyInfo(alias="questionsPerTest")]
    """Number of questions per test"""

    randomize_answers: Annotated[bool, PropertyInfo(alias="randomizeAnswers")]
    """Randomize answer order"""

    randomize_questions: Annotated[bool, PropertyInfo(alias="randomizeQuestions")]
    """Randomize question order"""

    show_correct_answers: Annotated[bool, PropertyInfo(alias="showCorrectAnswers")]
    """Show correct answers after submission"""

    show_explanations: Annotated[bool, PropertyInfo(alias="showExplanations")]
    """Show explanations for answers"""

    time_limit: Annotated[float, PropertyInfo(alias="timeLimit")]
    """Time limit in minutes"""


class ConfigAudioRecapConfigDto(TypedDict, total=False):
    duration: float
    """Duration of audio recap in minutes"""

    folders: List[str]
    """Folder IDs"""

    is_multi_voice: Annotated[bool, PropertyInfo(alias="isMultiVoice")]
    """Enable multi-voice conversation mode"""

    materials: List[str]
    """Material IDs"""

    model: str
    """AI model to use for generation"""

    num_parts: Annotated[float, PropertyInfo(alias="numParts")]
    """Number of parts to split the audio into"""

    recap_type: Annotated[Literal["SUMMARY", "LECTURE", "PODCAST", "AUDIO_BOOK"], PropertyInfo(alias="recapType")]
    """Type of audio recap"""

    theme: str
    """Theme or style for the audio recap"""

    topic: str
    """Specific topic to focus on"""

    voice1: str
    """Primary voice for narration"""

    voice2: str
    """Secondary voice for multi-voice mode"""


class ConfigExplainersConfigDto(TypedDict, total=False):
    folders: List[str]
    """Folder IDs"""

    image_search: Annotated[bool, PropertyInfo(alias="imageSearch")]
    """Enable image search for visuals"""

    materials: List[str]
    """Material IDs"""

    model: str
    """AI model to use for generation"""

    style: str
    """Video style"""

    target_length: Annotated[float, PropertyInfo(alias="targetLength")]
    """Target length in seconds"""

    title: str
    """Video title (defaults to component name if not provided)"""

    vertical_video: Annotated[bool, PropertyInfo(alias="verticalVideo")]
    """Create vertical video format (9:16)"""

    web_search: Annotated[bool, PropertyInfo(alias="webSearch")]
    """Enable web search for additional content"""


class ConfigUploadsConfigDto(TypedDict, total=False):
    folder_id: Required[Annotated[str, PropertyInfo(alias="folderId")]]
    """Folder ID where uploads will be stored"""

    folders: List[str]
    """Folder IDs"""

    materials: List[str]
    """Material IDs"""


class ConfigTutorMeConfigDto(TypedDict, total=False):
    enable_video: Annotated[bool, PropertyInfo(alias="enableVideo")]
    """Enable video"""

    enable_voice: Annotated[bool, PropertyInfo(alias="enableVoice")]
    """Enable voice"""

    folders: List[str]
    """Folder IDs"""

    materials: List[str]
    """Material IDs"""

    session_duration: Annotated[float, PropertyInfo(alias="sessionDuration")]
    """Session duration in minutes"""

    tutor_personality: Annotated[str, PropertyInfo(alias="tutorPersonality")]
    """Tutor personality"""


class ConfigChatAnalyticsConfigDto(TypedDict, total=False):
    chat_component_id: Required[Annotated[str, PropertyInfo(alias="chatComponentId")]]
    """ID of the chat component to analyze"""

    auto_refresh: Annotated[bool, PropertyInfo(alias="autoRefresh")]
    """Enable auto-refresh"""

    date_range: Annotated[float, PropertyInfo(alias="dateRange")]
    """Default date range in days"""

    enable_export: Annotated[bool, PropertyInfo(alias="enableExport")]
    """Enable CSV export functionality"""

    refresh_interval: Annotated[float, PropertyInfo(alias="refreshInterval")]
    """Refresh interval in minutes"""

    show_summary: Annotated[bool, PropertyInfo(alias="showSummary")]
    """Show summary section"""

    show_topics: Annotated[bool, PropertyInfo(alias="showTopics")]
    """Show top topics"""

    show_user_stats: Annotated[bool, PropertyInfo(alias="showUserStats")]
    """Show user statistics section"""


Config: TypeAlias = Union[
    ConfigChatConfigDto,
    ConfigDataAnalystConfigDto,
    ConfigFlashcardsConfigDto,
    ConfigScenariosConfigDto,
    ConfigPracticeTestConfigDto,
    ConfigAudioRecapConfigDto,
    ConfigExplainersConfigDto,
    ConfigUploadsConfigDto,
    ConfigTutorMeConfigDto,
    ConfigChatAnalyticsConfigDto,
]
