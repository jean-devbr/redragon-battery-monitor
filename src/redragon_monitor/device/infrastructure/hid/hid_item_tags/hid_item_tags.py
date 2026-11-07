class HidItemTags:
    LONG_ITEM = 0xFE
    TYPE_MAIN = 0
    TYPE_GLOBAL = 1
    MAIN_INPUT = 0x8
    MAIN_OUTPUT = 0x9
    GLOBAL_PUSH = 0xA
    GLOBAL_POP = 0xB
    GLOBAL_FIELDS = {0x0: "page", 0x7: "size", 0x8: "id", 0x9: "count"}
    SIZES = (0, 1, 2, 4)
