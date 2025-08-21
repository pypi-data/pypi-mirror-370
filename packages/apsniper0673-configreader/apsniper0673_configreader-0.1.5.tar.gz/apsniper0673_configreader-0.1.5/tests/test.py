from configreader.config_reader import ConfigReader

config = ConfigReader()
config.set_section()

section = config.get_section()

for key, value in section.items():
    print(f"{key}: {value}")