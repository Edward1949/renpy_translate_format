# game/scripts/sample.rpy:1
translate english sample_start_a1b2c3d4:

    # "This is an English line."
    ""

# game/scripts/sample.rpy:5
translate english sample_mid_5e6f7g8h:

    # Obi Wan "Hello there!"
    Obi Wan ""

# game/scripts/sample.rpy:9
translate english sample_end_9i0j1k2l:

    # "The end." with vpunch
    Obi Wan "" with vpunch

translate english strings:

    # renpy/common/00accessibility.rpy:28
    old "Self-voicing disabled."
    new ""

    # renpy/common/00accessibility.rpy:29
    old "Clipboard voicing enabled. "
    new ""

    # renpy/common/00accessibility.rpy:30
    old "Self-voicing enabled. "
    new ""

    # renpy/common/00accessibility.rpy:31
    old "Clipboard voicing disabled. "
    new ""

    # 以下条目在英文中缺失，用于测试追加功能
    old "I hope I sleep well."
    new ""

    old "Click to continue."
    new ""