#! /bin/sh
#
# Copyright (c) 2006 Matthieu Herrb
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
# Some updates by Brian Paul
# XCB update and some cleanup by Peter Hutterer


#gitbase="git://git.freedesktop.org/git"
gitbase="http://anongit.freedesktop.org/git"

#app="appres bdftopcf beforelight bitmap compiz constype editres fonttosfnt\
#	fslsfonts fstobdf glxcompmgr iceauth ico lbxproxy listres luit\
#	makepsres mkcfm mkfontdir mkfontscale oclock pclcomp proxymngr\
#	rendercheck rgb rstart scripts sessreg setxkbmap showfont smproxy\
#	twm viewres x11perf xauth xbiff xcalc xclipboard xclock xcmsdb\
#	xcompmgr xconsole xcursorgen xdbedizzy xditview xdm xdpyinfo\
#	xdriinfo xedit xev xeyes xf86dga xfd xfindproxy xfontsel xfs\
#	xfsinfo xfwp xgamma xgc xhost xinit xinput xkbcomp xkbevd xkbprint\
#	xkbutils xkill xload xlogo xlsatoms xlsclients xlsfonts xmag\
#	xman xmessage xmh xmodmap xmore xphelloworld xplsprinters xpr\
#	xprehashprinterlist xprop xrandr xrdb xrefresh xrestop xrx xset\
#	xsetmode xsetpointer xsetroot xshowdamage xsm xstdcmap xtrap \
#	xvidtune xvinfo xwd xwininfo xwud"
app="xrandr"
data="bitmaps cursors"

doc="xorg-docs xorg-sgml-doctools"
driver="xf86-input-evdev"
#driver="xf86-input-acecad xf86-input-aiptek xf86-input-calcomp\
#	xf86-input-citron xf86-input-digitaledge xf86-input-dmc\
#	xf86-input-dynapro xf86-input-elo2300 xf86-input-elographics\
#	xf86-input-evdev xf86-input-fpit xf86-input-hyperpen\
#	xf86-input-jamstudio xf86-input-joystick xf86-input-keyboard\
#	xf86-input-magellan xf86-input-magictouch xf86-input-microtouch\
#	xf86-input-mouse xf86-input-mutouch xf86-input-palmax\
#	xf86-input-penmount xf86-input-sample xf86-input-spaceorb\
#	xf86-input-summa xf86-input-tek4957 xf86-input-ur98\
#	xf86-input-vmmouse xf86-input-void xf86-video-apm\
#	xf86-video-ark xf86-video-ast xf86-video-ati\
#	xf86-video-chips xf86-video-cirrus xf86-video-cyrix\
#	xf86-video-dummy xf86-video-fbdev xf86-video-glide\
#	xf86-video-glint xf86-video-i128 xf86-video-i740\
#	xf86-video-impact xf86-video-imstt xf86-video-intel\
#	xf86-video-mga xf86-video-neomagic xf86-video-newport\
#	xf86-video-nsc xf86-video-nv xf86-video-rendition\
#	xf86-video-s3 xf86-video-s3virge xf86-video-savage\
#	xf86-video-siliconmotion xf86-video-sis xf86-video-sisusb\
#	xf86-video-sunbw2 xf86-video-suncg14 xf86-video-suncg3\
#	xf86-video-suncg6 xf86-video-sunffb xf86-video-sunleo\
#	xf86-video-suntcx xf86-video-tdfx xf86-video-tga\
#	xf86-video-trident xf86-video-tseng xf86-video-v4l\
#	xf86-video-vesa xf86-video-vga xf86-video-via\
#	xf86-video-vmware xf86-video-voodoo xf86-video-wsfb"
#
font="adobe-100dpi adobe-75dpi adobe-utopia-100dpi adobe-utopia-75dpi\
	adobe-utopia-type1 alias arabic-misc bh-100dpi bh-75dpi\
	bh-lucidatypewriter-100dpi bh-lucidatypewriter-75dpi\
	bh-ttf bh-type1 bitstream-100dpi bitstream-75dpi\
	bitstream-speedo bitstream-type1 cronyx-cyrillic\
	cursor-misc daewoo-misc dec-misc encodings ibm-type1\
	isas-misc jis-misc micro-misc misc-cyrillic misc-ethiopic\
	misc-meltho misc-misc mutt-misc schumacher-misc \
	screen-cyrillic sony-misc sun-misc util winitzki-cyrillic\
	xfree86-type1"

#lib="libAppleWM libFS libICE libSM libWindowsWM libX11 libXRes\
#	libXScrnSaver libXTrap libXau libXaw libXcomposite libXcursor\
#	libXdamage libXdmcp libXevie libXext libXfixes libXfont\
#	libXfontcache libXft libXi libXinerama libXmu libXp\
#	libXpm libXprintAppUtil libXprintUtil libXrandr libXrender\
#	libXt libXtst libXv libXvMC libXxf86dga libXxf86misc\
#	libXxf86rush libXxf86vm libdmx libfontenc liblbxutil\
#	liboldX libpciaccess libxkbfile libxkbui libxtrans libevdev libxshmfence"
lib="libXrandr libXext libX11 libpciaccess libXv libXdmcp libevdev libxshmfence libxtrans libXdamage libXfixes libXrender libfontenc libXfont"

proto="applewmproto bigreqsproto compositeproto damageproto\
	dri2proto dmxproto evieproto fixesproto fontcacheproto\
	fontsproto glproto inputproto kbproto panoramixproto\
	pmproto printproto randrproto recordproto renderproto\
	resourceproto scrnsaverproto trapproto videoproto \
	windowswmproto x11proto xcmiscproto xextproto\
	xf86bigfontproto xf86dgaproto xf86driproto xf86miscproto\
	xf86rushproto xf86vidmodeproto xineramaproto presentproto dri2proto"
#proto="dri2proto randrproto inputproto renderproto xextproto recordproto x11proto xcmiscproto bigreqsproto xf86driproto xf86vidmodeproto"

util="macros modular"
#util="cf gccmakedep imake install-check lndir macros makedepend\
#	modular xmkmf"

xcb="proto libxcb pthread-stubs"

# $1 is the main project path in the git repository (e.g. xorg).
# $2 is the module's directory (e.g. lib)
# $3 is the module name (e.g. libXi)
# $1 and $2 can be '.', in which case they are ignored.
# The path for git clone will be $gitbase/$1/$2/$3 
do_dir () {
	dir=$2
	if [ ! -d ${dir} ]; then 
		echo "creating ${dir}"
		mkdir -p ${dir}
	fi
	for d in $3; do 
		if [ -d "${dir}/$d" ]; then
			echo "${dir}/$d exists, pulling"
			(cd "${dir}/$d" ; 
                         git reset --hard HEAD ||return 1
                         git clean -x -d
                         if [ $? -eq 128 ]; then
                            git clean -x -d | grep clean.requireForce
                            if [ $? -eq 1 ]; then
                              git clean -x -d -f || return 1
                            else
                              return 1
                            fi
                         fi
                         git checkout master && git pull)
#			 if [ "$d" == "macros" ]; then
#				git reset --hard 61f5a48a74680c316bee2bf93d6ef5d50a688f22
#			 fi)
			
		else
			echo "cloning ${dir}/${d}"
	                if [ $1 = '.' ] ; then
	                    src="${gitbase}"
	                else
	                    src="${gitbase}/$1"
	                fi

			if [ ${dir} = '.' ] ; then
				src="${src}/$d"
			else
				src="${src}/${dir}/$d"
			fi
			(cd "${dir}" ; git clone ${src})
			
		fi
	done
}

do_dir xorg app "${app}"
#do_dir xorg data "${data}"
#do_dir xorg doc "${doc}"
do_dir xorg driver "${driver}"
do_dir xorg lib "${lib}"
do_dir xorg proto "${proto}"
do_dir xorg util "${util}"
do_dir . . pixman
#do_dir xorg . xserver
#do_dir mesa . drm
do_dir . xcb "${xcb}"
