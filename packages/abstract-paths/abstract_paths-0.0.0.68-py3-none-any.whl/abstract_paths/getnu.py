ls = []
for each in """root      840376  2.7  1.4 1907836 1901656 ?     Ss   Nov08  61:36 /sbin/mount.ntfs /dev/sde2 /mnt/16T -o rw
root      965957  0.0  0.0  17144  6784 pts/30   T+   Nov09   0:00 sudo rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      965960  0.0  0.0  17144  2624 pts/32   Ss+  Nov09   0:00 sudo rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      965961  0.0  0.0  18920 12288 pts/32   T    Nov09   0:03 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      965962  0.0  0.0  18960 10468 pts/32   T    Nov09   0:03 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      965963  0.0  0.0 199292 28004 pts/32   T    Nov09   0:00 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966174  0.0  0.0  17152  6784 ?        S    Nov09   0:00 sudo rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966175  0.2  0.2 317172 296140 ?       S    Nov09   1:43 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966176  0.1  0.1 282840 258292 ?       S    Nov09   1:03 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966177  0.1  0.4 13632896 528844 ?     S    Nov09   1:22 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966187  0.0  0.0  17144  6656 pts/33   T+   Nov09   0:00 sudo rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966190  0.0  0.0  17144  2568 pts/35   Ss+  Nov09   0:00 sudo rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966191  0.0  0.0  19184 12168 pts/35   T    Nov09   0:01 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966192  0.0  0.0  17940  8932 pts/35   T    Nov09   0:00 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966193  0.0  0.0 199036 11436 pts/35   T    Nov09   0:00 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966286  0.0  0.0  17148  6784 ?        S    Nov09   0:00 sudo rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966287  0.2  0.2 316596 295244 ?       S    Nov09   1:39 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966288  0.1  0.1 282800 258008 ?       S    Nov09   1:01 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966289  0.1  0.4 13632868 537232 ?     S    Nov09   1:18 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966299  0.0  0.0  17144  6784 ?        S    Nov09   0:00 sudo rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966302  0.0  0.0  17144  2496 pts/38   Ss+  Nov09   0:00 sudo rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966303  0.2  0.2 316596 295412 pts/38  S    Nov09   1:37 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966304  0.1  0.1 282800 257688 pts/38  S    Nov09   1:01 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966305  0.1  0.4 13632868 535764 pts/38 S   Nov09   1:18 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966386  0.0  0.0  17144  6656 ?        S    Nov09   0:00 sudo rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966387  0.2  0.2 316600 295176 ?       S    Nov09   1:36 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966388  0.1  0.1 282800 257500 ?       S    Nov09   1:02 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966389  0.1  0.4 13632868 566340 ?     S    Nov09   1:17 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966457  0.0  0.0  17152  6656 ?        S    Nov09   0:00 sudo rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966460  0.0  0.0  17152  2500 pts/40   Ss+  Nov09   0:00 sudo rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966461  0.2  0.2 316600 295180 pts/40  S    Nov09   1:57 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966462  0.1  0.1 282800 257928 pts/40  S    Nov09   1:05 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
root      966463  0.1  0.4 13632868 570340 pts/40 S   Nov09   1:17 rsync -avh --ignore-existing --progress --exclude node_modules /mnt/16T/evo980-new/ /mnt/24T/wd_main_980/
""".split('\n'):
  if each:
    ls.append([ea for ea in each.split(' ') if ea][1])
input(' '.join(ls))
