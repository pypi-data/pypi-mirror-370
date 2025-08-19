import shutil

MAP_BUILDER = {
    "java": ["maven", "mvn", "gradle", "gradlew", "make"],
    "cpp": ["cmake", "make"],
    "c":["make"],
    "rust": ["cargo"],
    "python": "python"
}

MAP_LANGUAGE_FILES = {
    "java": ["pom.xml", "build.gradle", "Makefile"],
    "cpp": ["CMakeLists.txt", "Makefile"],
    "c": ["Makefile"],
    "rust": ["Cargo.toml"],
    "python": ["pyproject.toml", "setup.py"]
}

MAP_FILE_LANGUAGE = {file: lang for lang, files in MAP_LANGUAGE_FILES.items() for file in files}


def check_available_builder_for_language(language):
    builders = MAP_BUILDER.get(language)
    return any([shutil.which(b) for b in builders])
