#!/usr/bin/perl

use strict;
use warnings;

# Configuration
my $FB_DEV = "/dev/fb0";
my $INPUT_DEV = "/dev/input/event2"; # Power Key
my $WIDTH  = 128;
my $HEIGHT = 128;
my $BPP    = 2; # 16 bits

# Colors (RGB565)
my $COLOR_RED   = pack("S", 0xF800);
my $COLOR_GREEN = pack("S", 0x07E0);
my $COLOR_BLUE  = pack("S", 0x001F);
my $COLOR_BLACK = pack("S", 0x0000);

print "[-] Opening Framebuffer...\n";
sysopen(my $fb, $FB_DEV, 2) or die "Cannot open $FB_DEV: $!";

print "[-] Opening Input Device ($INPUT_DEV)...";
sysopen(my $input, $INPUT_DEV, 0) or die "Cannot open $INPUT_DEV: $!"; # 0 = O_RDONLY

sub draw_rect {
    my ($x, $y, $w, $h, $color) = @_;
    for my $row ($y .. $y + $h - 1) {
        next if $row >= $HEIGHT;
        my $offset = ($row * $WIDTH + $x) * $BPP;
        sysseek($fb, $offset, 0);
        my $line_data = $color x $w;
        syswrite($fb, $line_data, length($line_data));
    }
}

sub clear_screen {
    my ($color) = @_; 
    draw_rect(0, 0, $WIDTH, $HEIGHT, $color);
}

# Initial State
print "[-] Starting Event Loop. Press POWER to toggle Green/Blue.\n";
clear_screen($COLOR_BLUE);
my $state = 0;

my $event_size = 16; # 32-bit arch input_event struct size
my $buffer;

while (sysread($input, $buffer, $event_size)) {
    # Unpack struct: L (sec), L (usec), S (type), S (code), i (value)
    my ($sec, $usec, $type, $code, $value) = unpack("LLSSi", $buffer);

    # Type 1 = EV_KEY
    # Code 116 = KEY_POWER (Check your specific keycode if this fails, usually 116)
    # Value 1 = Press, 0 = Release

    if ($type == 1 && $value == 1) {
        print "[+] Button Pressed! Code: $code\n";
        
        if ($state == 0) {
            clear_screen($COLOR_GREEN);
            $state = 1;
        } else {
            clear_screen($COLOR_BLUE);
            $state = 0;
        }
    }
}

close($fb);
close($input);