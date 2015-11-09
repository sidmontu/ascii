# coding: utf-8
# USAGE: ruby ttf2png.rb

#//-------------------------------------------
# Note:
#//-------------------------------------------

# Unicode(code point):
# U+3042 == "あ" == "\u3042" == \u{3042}

# How to get code point:
# "あ".unpack( "U*" ).first.to_s(16)  #=> "3042"
# "あ".encode( "UTF-8" ).ord.to_s(16) #=> "3042"

#//-------------------------------------------
# Config:
#//-------------------------------------------

FONT      = "courier.ttf"
FONT_SIZE = "12x24" #pt

FIRST     = "\u0020"  # == "あ"
LAST      = "\u007e"  # == "ヺ"

#//-------------------------------------------
COUNT	= 32
(FIRST..LAST).step do |a|
  cmd = "convert -background white -fill black -font #{FONT} -gravity Center  -size #{FONT_SIZE} label:\"#{a}\" #{COUNT}.png"
  puts cmd
  COUNT = COUNT + 1
  system(cmd) if ARGV[0]
end

print sprintf("If you want to execute these commands, try this: \nruby %s 1\n", File.basename(__FILE__)) if ARGV.length == 0
