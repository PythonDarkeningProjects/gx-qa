#!/bin/sh
# grub menuentry cleanup
TMP=$(mktemp)
grep -A 30 ^menuentry\ \'Ubuntu\'  /boot/grub/grub.cfg | grep -B 30 ^} >$TMP
UUID=$(grep root=UUID= $TMP | head -1); set $UUID
UUID=$(echo "$3" | cut -b 11-)

cat <<EOF >/etc/grub.d/40_ezbench-kernel
#!/bin/sh
exec tail -n +3 \$0
menuentry 'ezbench_kernel' {
load_video
insmod gzio
insmod part_msdos
insmod ext2
linux   /boot/linux-ezbench root=UUID=$UUID \$vt_handoff intel_iommu=igfx_off ro
initrd  /boot/linux-ezbench_initrd.img
}
EOF

chmod a+x /etc/grub.d/40_ezbench-kernel
update-grub2
