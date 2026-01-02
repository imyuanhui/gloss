from enum import Enum

class MeaningType(str, Enum):
    CORE_LEXICAL="Core Lexical"
    # Meaning that relies on shared cultural knowledge or references
    CULTURAL_LITERACY = "Cultural-Literacy"

    # A derived or extended meaning branching from the core sense
    POLYSEMOUS_EXTENSION = "Polysemous Extension"

    # Informal, slang, or conversational usage
    COLLOQUIAL_SLANG = "Colloquial / Slang"

    # Specialized usage in formal, scientific, or academic contexts
    TECHNICAL_ACADEMIC = "Technical / Academic"

