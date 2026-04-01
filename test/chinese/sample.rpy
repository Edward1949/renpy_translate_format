# game/scripts/sample.rpy:1
translate chinese sample_start_a1b2c3d4:

    # "This is an English line."
    "这是一行中文翻译。"

# game/scripts/sample.rpy:5
translate chinese sample_mid_5e6f7g8h:

    # Obi Wan "Hello there!"
    Obi Wan "你好！"

# game/scripts/sample.rpy:9
translate chinese sample_end_9i0j1k2l:

    # "The end."
    Obi Wan "结束。" with vpunch

# game/scripts/sample.rpy:13
translate chinese sample_strings_block:

    # 注释：这是一个字符串翻译块示例
    old "I hope I sleep well."
    new "希望我能睡个好觉。"

    old "Click to continue."
    new "点击继续。"

    # 另一条注释
    old "Self-voicing disabled."
    new "自发声已禁用。"

    old "This string only exists in Chinese."
    new "这个字符串只存在于中文中，测试追加功能。"