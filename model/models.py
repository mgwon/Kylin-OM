# from django.db import models
# import pandas as pd
# from django.db import models
#
# df1 = pd.read_csv('2024-07-17systeminfo.csv')
# df2 = pd.read_csv('2024-07-17processinfo.csv')
# internum = int((df1.shape[1] - 30) / 6)
#
# class mysysteminfo(models.Model):
#
#     timestamp = models.CharField(max_length=32)
#     CPUlogics_num = models.CharField(max_length=32)
#     CPUphysicals_num = models.CharField(max_length=32)
#     CPU_usage = models.CharField(max_length=32)
#     CPU_freq = models.CharField(max_length=32)
#     UserMode_runtime = models.CharField(max_length=32)
#
#     CoreState_runtime = models.CharField(max_length=32)
#     IOwait_time = models.CharField(max_length=32)
#     Averload_in1min = models.CharField(max_length=32)
#     Averload_in5min = models.CharField(max_length=32)
#     Averload_in15min = models.CharField(max_length=32)
#     interruptions_num = models.CharField(max_length=32)
#     softinterruptions_num = models.CharField(max_length=32)
#     systemcalls_num = models.CharField(max_length=32)
#
#     Totalmemory_size = models.CharField(max_length=32)
#     Usedmemory_size = models.CharField(max_length=32)
#     Freememory_size = models.CharField(max_length=32)
#     Memory_usage = models.CharField(max_length=32)
#     Swapmemory_size = models.CharField(max_length=32)
#     UsedSwapmemory_size = models.CharField(max_length=32)
#     FreeSwapmemory_size = models.CharField(max_length=32)
#     Swapmemory_usage = models.CharField(max_length=32)
#
#     Totaldisk_size = models.CharField(max_length=32)
#     Useddisk_size = models.CharField(max_length=32)
#     Freedisk_size = models.CharField(max_length=32)
#     Disk_usage = models.CharField(max_length=32)
#     readIO_size = models.CharField(max_length=32)
#     writeIO_size = models.CharField(max_length=32)
#     readdisk_time = models.CharField(max_length=32)
#     writedisk_time = models.CharField(max_length=32)
#
#     if internum==1:
#         nic1_datasent_size = models.CharField(max_length=32)
#         nic1_datasent_num = models.CharField(max_length=32)
#         nic1_datareceived_size = models.CharField(max_length=32)
#         nic1_datareceived_num = models.CharField(max_length=32)
#         nic1_datareceived_error = models.CharField(max_length=32)
#         nic1_datasent_error = models.CharField(max_length=32)
#
#
#     elif internum==2:
#         nic1_datasent_size = models.CharField(max_length=32)
#         nic1_datasent_num = models.CharField(max_length=32)
#         nic1_datareceived_size = models.CharField(max_length=32)
#         nic1_datareceived_num = models.CharField(max_length=32)
#         nic1_datareceived_error = models.CharField(max_length=32)
#         nic1_datasent_error = models.CharField(max_length=32)
#         nic2_datasent_size = models.CharField(max_length=32)
#         nic2_datasent_num = models.CharField(max_length=32)
#         nic2_datareceived_size = models.CharField(max_length=32)
#         nic2_datareceived_num = models.CharField(max_length=32)
#         nic2_datareceived_error = models.CharField(max_length=32)
#         nic2_datasent_error = models.CharField(max_length=32)
#
#
#
#     elif internum == 3:
#         nic1_datasent_size = models.CharField(max_length=32)
#         nic1_datasent_num = models.CharField(max_length=32)
#         nic1_datareceived_size = models.CharField(max_length=32)
#         nic1_datareceived_num = models.CharField(max_length=32)
#         nic1_datareceived_error = models.CharField(max_length=32)
#         nic1_datasent_error = models.CharField(max_length=32)
#         nic2_datasent_size = models.CharField(max_length=32)
#         nic2_datasent_num = models.CharField(max_length=32)
#         nic2_datareceived_size = models.CharField(max_length=32)
#         nic2_datareceived_num = models.CharField(max_length=32)
#         nic2_datareceived_error = models.CharField(max_length=32)
#         nic2_datasent_error = models.CharField(max_length=32)
#         nic3_datasent_size = models.CharField(max_length=32)
#         nic3_datasent_num = models.CharField(max_length=32)
#         nic3_datareceived_size = models.CharField(max_length=32)
#         nic3_datareceived_num = models.CharField(max_length=32)
#         nic3_datareceived_error = models.CharField(max_length=32)
#         nic3_datasent_error = models.CharField(max_length=32)
#
#
#     elif internum == 4:
#         nic1_datasent_size = models.CharField(max_length=32)
#         nic1_datasent_num = models.CharField(max_length=32)
#         nic1_datareceived_size = models.CharField(max_length=32)
#         nic1_datareceived_num = models.CharField(max_length=32)
#         nic1_datareceived_error = models.CharField(max_length=32)
#         nic1_datasent_error = models.CharField(max_length=32)
#         nic2_datasent_size = models.CharField(max_length=32)
#         nic2_datasent_num = models.CharField(max_length=32)
#         nic2_datareceived_size = models.CharField(max_length=32)
#         nic2_datareceived_num = models.CharField(max_length=32)
#         nic2_datareceived_error = models.CharField(max_length=32)
#         nic2_datasent_error = models.CharField(max_length=32)
#         nic3_datasent_size = models.CharField(max_length=32)
#         nic3_datasent_num = models.CharField(max_length=32)
#         nic3_datareceived_size = models.CharField(max_length=32)
#         nic3_datareceived_num = models.CharField(max_length=32)
#         nic3_datareceived_error = models.CharField(max_length=32)
#         nic3_datasent_error = models.CharField(max_length=32)
#         nic4_datasent_size = models.CharField(max_length=32)
#         nic4_datasent_num = models.CharField(max_length=32)
#         nic4_datareceived_size = models.CharField(max_length=32)
#         nic4_datareceived_num = models.CharField(max_length=32)
#         nic4_datareceived_error = models.CharField(max_length=32)
#         nic4_datasent_error = models.CharField(max_length=32)
#
#
#     elif internum == 5:
#         nic1_datasent_size = models.CharField(max_length=32)
#         nic1_datasent_num = models.CharField(max_length=32)
#         nic1_datareceived_size = models.CharField(max_length=32)
#         nic1_datareceived_num = models.CharField(max_length=32)
#         nic1_datareceived_error = models.CharField(max_length=32)
#         nic1_datasent_error = models.CharField(max_length=32)
#         nic2_datasent_size = models.CharField(max_length=32)
#         nic2_datasent_num = models.CharField(max_length=32)
#         nic2_datareceived_size = models.CharField(max_length=32)
#         nic2_datareceived_num = models.CharField(max_length=32)
#         nic2_datareceived_error = models.CharField(max_length=32)
#         nic2_datasent_error = models.CharField(max_length=32)
#         nic3_datasent_size = models.CharField(max_length=32)
#         nic3_datasent_num = models.CharField(max_length=32)
#         nic3_datareceived_size = models.CharField(max_length=32)
#         nic3_datareceived_num = models.CharField(max_length=32)
#         nic3_datareceived_error = models.CharField(max_length=32)
#         nic3_datasent_error = models.CharField(max_length=32)
#         nic4_datasent_size = models.CharField(max_length=32)
#         nic4_datasent_num = models.CharField(max_length=32)
#         nic4_datareceived_size = models.CharField(max_length=32)
#         nic4_datareceived_num = models.CharField(max_length=32)
#         nic4_datareceived_error = models.CharField(max_length=32)
#         nic4_datasent_error = models.CharField(max_length=32)
#         nic5_datasent_size = models.CharField(max_length=32)
#         nic5_datasent_num = models.CharField(max_length=32)
#         nic5_datareceived_size = models.CharField(max_length=32)
#         nic5_datareceived_num = models.CharField(max_length=32)
#         nic5_datareceived_error = models.CharField(max_length=32)
#         nic5_datasent_error = models.CharField(max_length=32)
#
#
#     elif internum == 6:
#         nic1_datasent_size = models.CharField(max_length=32)
#         nic1_datasent_num = models.CharField(max_length=32)
#         nic1_datareceived_size = models.CharField(max_length=32)
#         nic1_datareceived_num = models.CharField(max_length=32)
#         nic1_datareceived_error = models.CharField(max_length=32)
#         nic1_datasent_error = models.CharField(max_length=32)
#         nic2_datasent_size = models.CharField(max_length=32)
#         nic2_datasent_num = models.CharField(max_length=32)
#         nic2_datareceived_size = models.CharField(max_length=32)
#         nic2_datareceived_num = models.CharField(max_length=32)
#         nic2_datareceived_error = models.CharField(max_length=32)
#         nic2_datasent_error = models.CharField(max_length=32)
#         nic3_datasent_size = models.CharField(max_length=32)
#         nic3_datasent_num = models.CharField(max_length=32)
#         nic3_datareceived_size = models.CharField(max_length=32)
#         nic3_datareceived_num = models.CharField(max_length=32)
#         nic3_datareceived_error = models.CharField(max_length=32)
#         nic3_datasent_error = models.CharField(max_length=32)
#         nic4_datasent_size = models.CharField(max_length=32)
#         nic4_datasent_num = models.CharField(max_length=32)
#         nic4_datareceived_size = models.CharField(max_length=32)
#         nic4_datareceived_num = models.CharField(max_length=32)
#         nic4_datareceived_error = models.CharField(max_length=32)
#         nic4_datasent_error = models.CharField(max_length=32)
#         nic5_datasent_size = models.CharField(max_length=32)
#         nic5_datasent_num = models.CharField(max_length=32)
#         nic5_datareceived_size = models.CharField(max_length=32)
#         nic5_datareceived_num = models.CharField(max_length=32)
#         nic5_datareceived_error = models.CharField(max_length=32)
#         nic5_datasent_error = models.CharField(max_length=32)
#         nic6_datasent_size = models.CharField(max_length=32)
#         nic6_datasent_num = models.CharField(max_length=32)
#         nic6_datareceived_size = models.CharField(max_length=32)
#         nic6_datareceived_num = models.CharField(max_length=32)
#         nic6_datareceived_error = models.CharField(max_length=32)
#         nic6_datasent_error = models.CharField(max_length=32)
#
#
#     elif internum == 7:
#         nic1_datasent_size = models.CharField(max_length=32)
#         nic1_datasent_num = models.CharField(max_length=32)
#         nic1_datareceived_size = models.CharField(max_length=32)
#         nic1_datareceived_num = models.CharField(max_length=32)
#         nic1_datareceived_error = models.CharField(max_length=32)
#         nic1_datasent_error = models.CharField(max_length=32)
#         nic2_datasent_size = models.CharField(max_length=32)
#         nic2_datasent_num = models.CharField(max_length=32)
#         nic2_datareceived_size = models.CharField(max_length=32)
#         nic2_datareceived_num = models.CharField(max_length=32)
#         nic2_datareceived_error = models.CharField(max_length=32)
#         nic2_datasent_error = models.CharField(max_length=32)
#         nic3_datasent_size = models.CharField(max_length=32)
#         nic3_datasent_num = models.CharField(max_length=32)
#         nic3_datareceived_size = models.CharField(max_length=32)
#         nic3_datareceived_num = models.CharField(max_length=32)
#         nic3_datareceived_error = models.CharField(max_length=32)
#         nic3_datasent_error = models.CharField(max_length=32)
#         nic4_datasent_size = models.CharField(max_length=32)
#         nic4_datasent_num = models.CharField(max_length=32)
#         nic4_datareceived_size = models.CharField(max_length=32)
#         nic4_datareceived_num = models.CharField(max_length=32)
#         nic4_datareceived_error = models.CharField(max_length=32)
#         nic4_datasent_error = models.CharField(max_length=32)
#         nic5_datasent_size = models.CharField(max_length=32)
#         nic5_datasent_num = models.CharField(max_length=32)
#         nic5_datareceived_size = models.CharField(max_length=32)
#         nic5_datareceived_num = models.CharField(max_length=32)
#         nic5_datareceived_error = models.CharField(max_length=32)
#         nic5_datasent_error = models.CharField(max_length=32)
#         nic6_datasent_size = models.CharField(max_length=32)
#         nic6_datasent_num = models.CharField(max_length=32)
#         nic6_datareceived_size = models.CharField(max_length=32)
#         nic6_datareceived_num = models.CharField(max_length=32)
#         nic6_datareceived_error = models.CharField(max_length=32)
#         nic6_datasent_error = models.CharField(max_length=32)
#         nic7_datasent_size = models.CharField(max_length=32)
#         nic7_datasent_num = models.CharField(max_length=32)
#         nic7_datareceived_size = models.CharField(max_length=32)
#         nic7_datareceived_num = models.CharField(max_length=32)
#         nic7_datareceived_error = models.CharField(max_length=32)
#         nic7_datasent_error = models.CharField(max_length=32)
#
#
#     elif internum == 8:
#         nic1_datasent_size = models.CharField(max_length=32)
#         nic1_datasent_num = models.CharField(max_length=32)
#         nic1_datareceived_size = models.CharField(max_length=32)
#         nic1_datareceived_num = models.CharField(max_length=32)
#         nic1_datareceived_error = models.CharField(max_length=32)
#         nic1_datasent_error = models.CharField(max_length=32)
#         nic2_datasent_size = models.CharField(max_length=32)
#         nic2_datasent_num = models.CharField(max_length=32)
#         nic2_datareceived_size = models.CharField(max_length=32)
#         nic2_datareceived_num = models.CharField(max_length=32)
#         nic2_datareceived_error = models.CharField(max_length=32)
#         nic2_datasent_error = models.CharField(max_length=32)
#         nic3_datasent_size = models.CharField(max_length=32)
#         nic3_datasent_num = models.CharField(max_length=32)
#         nic3_datareceived_size = models.CharField(max_length=32)
#         nic3_datareceived_num = models.CharField(max_length=32)
#         nic3_datareceived_error = models.CharField(max_length=32)
#         nic3_datasent_error = models.CharField(max_length=32)
#         nic4_datasent_size = models.CharField(max_length=32)
#         nic4_datasent_num = models.CharField(max_length=32)
#         nic4_datareceived_size = models.CharField(max_length=32)
#         nic4_datareceived_num = models.CharField(max_length=32)
#         nic4_datareceived_error = models.CharField(max_length=32)
#         nic4_datasent_error = models.CharField(max_length=32)
#         nic5_datasent_size = models.CharField(max_length=32)
#         nic5_datasent_num = models.CharField(max_length=32)
#         nic5_datareceived_size = models.CharField(max_length=32)
#         nic5_datareceived_num = models.CharField(max_length=32)
#         nic5_datareceived_error = models.CharField(max_length=32)
#         nic5_datasent_error = models.CharField(max_length=32)
#         nic6_datasent_size = models.CharField(max_length=32)
#         nic6_datasent_num = models.CharField(max_length=32)
#         nic6_datareceived_size = models.CharField(max_length=32)
#         nic6_datareceived_num = models.CharField(max_length=32)
#         nic6_datareceived_error = models.CharField(max_length=32)
#         nic6_datasent_error = models.CharField(max_length=32)
#         nic7_datasent_size = models.CharField(max_length=32)
#         nic7_datasent_num = models.CharField(max_length=32)
#         nic7_datareceived_size = models.CharField(max_length=32)
#         nic7_datareceived_num = models.CharField(max_length=32)
#         nic7_datareceived_error = models.CharField(max_length=32)
#         nic7_datasent_error = models.CharField(max_length=32)
#         nic8_datasent_size = models.CharField(max_length=32)
#         nic8_datasent_num = models.CharField(max_length=32)
#         nic8_datareceived_size = models.CharField(max_length=32)
#         nic8_datareceived_num = models.CharField(max_length=32)
#         nic8_datareceived_error = models.CharField(max_length=32)
#         nic8_datasent_error = models.CharField(max_length=32)
#
#
#     elif internum == 9:
#         nic1_datasent_size = models.CharField(max_length=32)
#         nic1_datasent_num = models.CharField(max_length=32)
#         nic1_datareceived_size = models.CharField(max_length=32)
#         nic1_datareceived_num = models.CharField(max_length=32)
#         nic1_datareceived_error = models.CharField(max_length=32)
#         nic1_datasent_error = models.CharField(max_length=32)
#         nic2_datasent_size = models.CharField(max_length=32)
#         nic2_datasent_num = models.CharField(max_length=32)
#         nic2_datareceived_size = models.CharField(max_length=32)
#         nic2_datareceived_num = models.CharField(max_length=32)
#         nic2_datareceived_error = models.CharField(max_length=32)
#         nic2_datasent_error = models.CharField(max_length=32)
#         nic3_datasent_size = models.CharField(max_length=32)
#         nic3_datasent_num = models.CharField(max_length=32)
#         nic3_datareceived_size = models.CharField(max_length=32)
#         nic3_datareceived_num = models.CharField(max_length=32)
#         nic3_datareceived_error = models.CharField(max_length=32)
#         nic3_datasent_error = models.CharField(max_length=32)
#         nic4_datasent_size = models.CharField(max_length=32)
#         nic4_datasent_num = models.CharField(max_length=32)
#         nic4_datareceived_size = models.CharField(max_length=32)
#         nic4_datareceived_num = models.CharField(max_length=32)
#         nic4_datareceived_error = models.CharField(max_length=32)
#         nic4_datasent_error = models.CharField(max_length=32)
#         nic5_datasent_size = models.CharField(max_length=32)
#         nic5_datasent_num = models.CharField(max_length=32)
#         nic5_datareceived_size = models.CharField(max_length=32)
#         nic5_datareceived_num = models.CharField(max_length=32)
#         nic5_datareceived_error = models.CharField(max_length=32)
#         nic5_datasent_error = models.CharField(max_length=32)
#         nic6_datasent_size = models.CharField(max_length=32)
#         nic6_datasent_num = models.CharField(max_length=32)
#         nic6_datareceived_size = models.CharField(max_length=32)
#         nic6_datareceived_num = models.CharField(max_length=32)
#         nic6_datareceived_error = models.CharField(max_length=32)
#         nic6_datasent_error = models.CharField(max_length=32)
#         nic7_datasent_size = models.CharField(max_length=32)
#         nic7_datasent_num = models.CharField(max_length=32)
#         nic7_datareceived_size = models.CharField(max_length=32)
#         nic7_datareceived_num = models.CharField(max_length=32)
#         nic7_datareceived_error = models.CharField(max_length=32)
#         nic7_datasent_error = models.CharField(max_length=32)
#         nic8_datasent_size = models.CharField(max_length=32)
#         nic8_datasent_num = models.CharField(max_length=32)
#         nic8_datareceived_size = models.CharField(max_length=32)
#         nic8_datareceived_num = models.CharField(max_length=32)
#         nic8_datareceived_error = models.CharField(max_length=32)
#         nic8_datasent_error = models.CharField(max_length=32)
#         nic9_datasent_size = models.CharField(max_length=32)
#         nic9_datasent_num = models.CharField(max_length=32)
#         nic9_datareceived_size = models.CharField(max_length=32)
#         nic9_datareceived_num = models.CharField(max_length=32)
#         nic9_datareceived_error = models.CharField(max_length=32)
#         nic9_datasent_error = models.CharField(max_length=32)
#
#
#     elif internum == 10:
#         nic1_datasent_size = models.CharField(max_length=32)
#         nic1_datasent_num = models.CharField(max_length=32)
#         nic1_datareceived_size = models.CharField(max_length=32)
#         nic1_datareceived_num = models.CharField(max_length=32)
#         nic1_datareceived_error = models.CharField(max_length=32)
#         nic1_datasent_error = models.CharField(max_length=32)
#         nic2_datasent_size = models.CharField(max_length=32)
#         nic2_datasent_num = models.CharField(max_length=32)
#         nic2_datareceived_size = models.CharField(max_length=32)
#         nic2_datareceived_num = models.CharField(max_length=32)
#         nic2_datareceived_error = models.CharField(max_length=32)
#         nic2_datasent_error = models.CharField(max_length=32)
#         nic3_datasent_size = models.CharField(max_length=32)
#         nic3_datasent_num = models.CharField(max_length=32)
#         nic3_datareceived_size = models.CharField(max_length=32)
#         nic3_datareceived_num = models.CharField(max_length=32)
#         nic3_datareceived_error = models.CharField(max_length=32)
#         nic3_datasent_error = models.CharField(max_length=32)
#         nic4_datasent_size = models.CharField(max_length=32)
#         nic4_datasent_num = models.CharField(max_length=32)
#         nic4_datareceived_size = models.CharField(max_length=32)
#         nic4_datareceived_num = models.CharField(max_length=32)
#         nic4_datareceived_error = models.CharField(max_length=32)
#         nic4_datasent_error = models.CharField(max_length=32)
#         nic5_datasent_size = models.CharField(max_length=32)
#         nic5_datasent_num = models.CharField(max_length=32)
#         nic5_datareceived_size = models.CharField(max_length=32)
#         nic5_datareceived_num = models.CharField(max_length=32)
#         nic5_datareceived_error = models.CharField(max_length=32)
#         nic5_datasent_error = models.CharField(max_length=32)
#         nic6_datasent_size = models.CharField(max_length=32)
#         nic6_datasent_num = models.CharField(max_length=32)
#         nic6_datareceived_size = models.CharField(max_length=32)
#         nic6_datareceived_num = models.CharField(max_length=32)
#         nic6_datareceived_error = models.CharField(max_length=32)
#         nic6_datasent_error = models.CharField(max_length=32)
#         nic7_datasent_size = models.CharField(max_length=32)
#         nic7_datasent_num = models.CharField(max_length=32)
#         nic7_datareceived_size = models.CharField(max_length=32)
#         nic7_datareceived_num = models.CharField(max_length=32)
#         nic7_datareceived_error = models.CharField(max_length=32)
#         nic7_datasent_error = models.CharField(max_length=32)
#         nic8_datasent_size = models.CharField(max_length=32)
#         nic8_datasent_num = models.CharField(max_length=32)
#         nic8_datareceived_size = models.CharField(max_length=32)
#         nic8_datareceived_num = models.CharField(max_length=32)
#         nic8_datareceived_error = models.CharField(max_length=32)
#         nic8_datasent_error = models.CharField(max_length=32)
#         nic9_datasent_size = models.CharField(max_length=32)
#         nic9_datasent_num = models.CharField(max_length=32)
#         nic9_datareceived_size = models.CharField(max_length=32)
#         nic9_datareceived_num = models.CharField(max_length=32)
#         nic9_datareceived_error = models.CharField(max_length=32)
#         nic9_datasent_error = models.CharField(max_length=32)
#         nic10_datasent_size = models.CharField(max_length=32)
#         nic10_datasent_num = models.CharField(max_length=32)
#         nic10_datareceived_size = models.CharField(max_length=32)
#         nic10_datareceived_num = models.CharField(max_length=32)
#         nic10_datareceived_error = models.CharField(max_length=32)
#         nic10_datasent_error = models.CharField(max_length=32)
#
#
#     elif internum == 11:
#         nic1_datasent_size = models.CharField(max_length=32)
#         nic1_datasent_num = models.CharField(max_length=32)
#         nic1_datareceived_size = models.CharField(max_length=32)
#         nic1_datareceived_num = models.CharField(max_length=32)
#         nic1_datareceived_error = models.CharField(max_length=32)
#         nic1_datasent_error = models.CharField(max_length=32)
#         nic2_datasent_size = models.CharField(max_length=32)
#         nic2_datasent_num = models.CharField(max_length=32)
#         nic2_datareceived_size = models.CharField(max_length=32)
#         nic2_datareceived_num = models.CharField(max_length=32)
#         nic2_datareceived_error = models.CharField(max_length=32)
#         nic2_datasent_error = models.CharField(max_length=32)
#         nic3_datasent_size = models.CharField(max_length=32)
#         nic3_datasent_num = models.CharField(max_length=32)
#         nic3_datareceived_size = models.CharField(max_length=32)
#         nic3_datareceived_num = models.CharField(max_length=32)
#         nic3_datareceived_error = models.CharField(max_length=32)
#         nic3_datasent_error = models.CharField(max_length=32)
#         nic4_datasent_size = models.CharField(max_length=32)
#         nic4_datasent_num = models.CharField(max_length=32)
#         nic4_datareceived_size = models.CharField(max_length=32)
#         nic4_datareceived_num = models.CharField(max_length=32)
#         nic4_datareceived_error = models.CharField(max_length=32)
#         nic4_datasent_error = models.CharField(max_length=32)
#         nic5_datasent_size = models.CharField(max_length=32)
#         nic5_datasent_num = models.CharField(max_length=32)
#         nic5_datareceived_size = models.CharField(max_length=32)
#         nic5_datareceived_num = models.CharField(max_length=32)
#         nic5_datareceived_error = models.CharField(max_length=32)
#         nic5_datasent_error = models.CharField(max_length=32)
#         nic6_datasent_size = models.CharField(max_length=32)
#         nic6_datasent_num = models.CharField(max_length=32)
#         nic6_datareceived_size = models.CharField(max_length=32)
#         nic6_datareceived_num = models.CharField(max_length=32)
#         nic6_datareceived_error = models.CharField(max_length=32)
#         nic6_datasent_error = models.CharField(max_length=32)
#         nic7_datasent_size = models.CharField(max_length=32)
#         nic7_datasent_num = models.CharField(max_length=32)
#         nic7_datareceived_size = models.CharField(max_length=32)
#         nic7_datareceived_num = models.CharField(max_length=32)
#         nic7_datareceived_error = models.CharField(max_length=32)
#         nic7_datasent_error = models.CharField(max_length=32)
#         nic8_datasent_size = models.CharField(max_length=32)
#         nic8_datasent_num = models.CharField(max_length=32)
#         nic8_datareceived_size = models.CharField(max_length=32)
#         nic8_datareceived_num = models.CharField(max_length=32)
#         nic8_datareceived_error = models.CharField(max_length=32)
#         nic8_datasent_error = models.CharField(max_length=32)
#         nic9_datasent_size = models.CharField(max_length=32)
#         nic9_datasent_num = models.CharField(max_length=32)
#         nic9_datareceived_size = models.CharField(max_length=32)
#         nic9_datareceived_num = models.CharField(max_length=32)
#         nic9_datareceived_error = models.CharField(max_length=32)
#         nic9_datasent_error = models.CharField(max_length=32)
#         nic10_datasent_size = models.CharField(max_length=32)
#         nic10_datasent_num = models.CharField(max_length=32)
#         nic10_datareceived_size = models.CharField(max_length=32)
#         nic10_datareceived_num = models.CharField(max_length=32)
#         nic10_datareceived_error = models.CharField(max_length=32)
#         nic10_datasent_error = models.CharField(max_length=32)
#         nic11_datasent_size = models.CharField(max_length=32)
#         nic11_datasent_num = models.CharField(max_length=32)
#         nic11_datareceived_size = models.CharField(max_length=32)
#         nic11_datareceived_num = models.CharField(max_length=32)
#         nic11_datareceived_error = models.CharField(max_length=32)
#         nic11_datasent_error = models.CharField(max_length=32)
#
#
#     elif internum == 12:
#         nic1_datasent_size = models.CharField(max_length=32)
#         nic1_datasent_num = models.CharField(max_length=32)
#         nic1_datareceived_size = models.CharField(max_length=32)
#         nic1_datareceived_num = models.CharField(max_length=32)
#         nic1_datareceived_error = models.CharField(max_length=32)
#         nic1_datasent_error = models.CharField(max_length=32)
#         nic2_datasent_size = models.CharField(max_length=32)
#         nic2_datasent_num = models.CharField(max_length=32)
#         nic2_datareceived_size = models.CharField(max_length=32)
#         nic2_datareceived_num = models.CharField(max_length=32)
#         nic2_datareceived_error = models.CharField(max_length=32)
#         nic2_datasent_error = models.CharField(max_length=32)
#         nic3_datasent_size = models.CharField(max_length=32)
#         nic3_datasent_num = models.CharField(max_length=32)
#         nic3_datareceived_size = models.CharField(max_length=32)
#         nic3_datareceived_num = models.CharField(max_length=32)
#         nic3_datareceived_error = models.CharField(max_length=32)
#         nic3_datasent_error = models.CharField(max_length=32)
#         nic4_datasent_size = models.CharField(max_length=32)
#         nic4_datasent_num = models.CharField(max_length=32)
#         nic4_datareceived_size = models.CharField(max_length=32)
#         nic4_datareceived_num = models.CharField(max_length=32)
#         nic4_datareceived_error = models.CharField(max_length=32)
#         nic4_datasent_error = models.CharField(max_length=32)
#         nic5_datasent_size = models.CharField(max_length=32)
#         nic5_datasent_num = models.CharField(max_length=32)
#         nic5_datareceived_size = models.CharField(max_length=32)
#         nic5_datareceived_num = models.CharField(max_length=32)
#         nic5_datareceived_error = models.CharField(max_length=32)
#         nic5_datasent_error = models.CharField(max_length=32)
#         nic6_datasent_size = models.CharField(max_length=32)
#         nic6_datasent_num = models.CharField(max_length=32)
#         nic6_datareceived_size = models.CharField(max_length=32)
#         nic6_datareceived_num = models.CharField(max_length=32)
#         nic6_datareceived_error = models.CharField(max_length=32)
#         nic6_datasent_error = models.CharField(max_length=32)
#         nic7_datasent_size = models.CharField(max_length=32)
#         nic7_datasent_num = models.CharField(max_length=32)
#         nic7_datareceived_size = models.CharField(max_length=32)
#         nic7_datareceived_num = models.CharField(max_length=32)
#         nic7_datareceived_error = models.CharField(max_length=32)
#         nic7_datasent_error = models.CharField(max_length=32)
#         nic8_datasent_size = models.CharField(max_length=32)
#         nic8_datasent_num = models.CharField(max_length=32)
#         nic8_datareceived_size = models.CharField(max_length=32)
#         nic8_datareceived_num = models.CharField(max_length=32)
#         nic8_datareceived_error = models.CharField(max_length=32)
#         nic8_datasent_error = models.CharField(max_length=32)
#         nic9_datasent_size = models.CharField(max_length=32)
#         nic9_datasent_num = models.CharField(max_length=32)
#         nic9_datareceived_size = models.CharField(max_length=32)
#         nic9_datareceived_num = models.CharField(max_length=32)
#         nic9_datareceived_error = models.CharField(max_length=32)
#         nic9_datasent_error = models.CharField(max_length=32)
#         nic10_datasent_size = models.CharField(max_length=32)
#         nic10_datasent_num = models.CharField(max_length=32)
#         nic10_datareceived_size = models.CharField(max_length=32)
#         nic10_datareceived_num = models.CharField(max_length=32)
#         nic10_datareceived_error = models.CharField(max_length=32)
#         nic10_datasent_error = models.CharField(max_length=32)
#         nic11_datasent_size = models.CharField(max_length=32)
#         nic11_datasent_num = models.CharField(max_length=32)
#         nic11_datareceived_size = models.CharField(max_length=32)
#         nic11_datareceived_num = models.CharField(max_length=32)
#         nic11_datareceived_error = models.CharField(max_length=32)
#         nic11_datasent_error = models.CharField(max_length=32)
#         nic12_datasent_size = models.CharField(max_length=32)
#         nic12_datasent_num = models.CharField(max_length=32)
#         nic12_datareceived_size = models.CharField(max_length=32)
#         nic12_datareceived_num = models.CharField(max_length=32)
#         nic12_datareceived_error = models.CharField(max_length=32)
#         nic12_datasent_error = models.CharField(max_length=32)
#
# class TimeRecord(models.Model):
#     start_time = models.DateTimeField(verbose_name='开始时间')
#     end_time = models.DateTimeField(verbose_name='结束时间')
#
#     def __str__(self):
#         return f"{self.start_time} - {self.end_time}"
#
# class myprocessinfo(models.Model):
#     timestamp_list = models.CharField(max_length=32)
#     name_list = models.CharField(max_length=128)
#     pid_list = models.CharField(max_length=32)
#     cpupercent_list = models.CharField(max_length=32)
#     mempercent_list = models.CharField(max_length=32)
#     status_list = models.CharField(max_length=32)
#     readbytes_list = models.CharField(max_length=32)
#     writebytes_list = models.CharField(max_length=32)
#     vms_list = models.CharField(max_length=32)
#     rss_list = models.CharField(max_length=32)
#     threads_list = models.CharField(max_length=32)
#     createtime_list = models.CharField(max_length=32)
#
# # order == 'delete'时删除数据库表内数据
# # order == 'create'时往数据库增添式拷贝csv内容
# def options(order):
#
#     if order == 'delete':
#         mysysteminfo.objects.all().delete()
#         myprocessinfo.objects.all().delete()
#     elif order == 'create':
#         h2 = df2.columns.tolist()
#         print(h2[1])
#         myprocessinfo.objects.create(
#             timestamp_list=h2[0],
#             name_list=h2[1],
#             pid_list=h2[2],
#             cpupercent_list=h2[3],
#             mempercent_list=h2[4],
#             status_list=h2[5],
#             readbytes_list=h2[6],
#             writebytes_list=h2[7],
#             vms_list=h2[8],
#             rss_list=h2[9],
#             threads_list=h2[10],
#             createtime_list=h2[11]
#         )
#         for y in df2.itertuples():
#             myprocessinfo.objects.create(
#                 timestamp_list=y[1],
#                 name_list=y[2],
#                 pid_list=y[3],
#                 cpupercent_list=y[4],
#                 mempercent_list=y[5],
#                 status_list=y[6],
#                 readbytes_list=y[7],
#                 writebytes_list=y[8],
#                 vms_list=y[9],
#                 rss_list=y[10],
#                 threads_list=y[11],
#                 createtime_list=y[12]
#             )
#
#         if internum == 1:
#             h1 = df1.columns.tolist()
#             mysysteminfo.objects.create(
#                 timestamp=h1[0],
#                 CPUlogics_num=h1[1],
#                 CPUphysicals_num=h1[2],
#                 CPU_usage=h1[3],
#                 CPU_freq=h1[4],
#                 UserMode_runtime=h1[5],
#                 CoreState_runtime=h1[6],
#                 IOwait_time=h1[7],
#                 Averload_in1min=h1[8],
#                 Averload_in5min=h1[9],
#                 Averload_in15min=h1[10],
#                 interruptions_num=h1[11],
#                 softinterruptions_num=h1[12],
#                 systemcalls_num=h1[13],
#
#                 Totalmemory_size=h1[14],
#                 Usedmemory_size=h1[15],
#                 Freememory_size=h1[16],
#                 Memory_usage=h1[17],
#                 Swapmemory_size=h1[18],
#                 UsedSwapmemory_size=h1[19],
#                 FreeSwapmemory_size=h1[20],
#                 Swapmemory_usage=h1[21],
#
#                 Totaldisk_size=h1[22],
#                 Useddisk_size=h1[23],
#                 Freedisk_size=h1[24],
#                 Disk_usage=h1[25],
#                 readIO_size=h1[26],
#                 writeIO_size=h1[27],
#                 readdisk_time=h1[28],
#                 writedisk_time=h1[29],
#                 nic1_datasent_size=h1[30],
#                 nic1_datasent_num=h1[31],
#                 nic1_datareceived_size=h1[32],
#                 nic1_datareceived_num=h1[33],
#                 nic1_datareceived_error=h1[34],
#                 nic1_datasent_error=h1[35]
#
#
#             )
#             for x in df1.itertuples():
#                 mysysteminfo.objects.create(
#                     timestamp=x[1],
#                     CPUlogics_num=x[2],
#                     CPUphysicals_num=x[3],
#                     CPU_usage=x[4],
#                     CPU_freq=x[5],
#                     UserMode_runtime=x[6],
#                     CoreState_runtime=x[7],
#                     IOwait_time=x[8],
#                     Averload_in1min=x[9],
#                     Averload_in5min=x[10],
#                     Averload_in15min=x[11],
#                     interruptions_num=x[12],
#                     softinterruptions_num=x[13],
#                     systemcalls_num=x[14],
#
#                     Totalmemory_size=x[15],
#                     Usedmemory_size=x[16],
#                     Freememory_size=x[17],
#                     Memory_usage=x[18],
#                     Swapmemory_size=x[19],
#                     UsedSwapmemory_size=x[20],
#                     FreeSwapmemory_size=x[21],
#                     Swapmemory_usage=x[22],
#
#                     Totaldisk_size=x[23],
#                     Useddisk_size=x[24],
#                     Freedisk_size=x[25],
#                     Disk_usage=x[26],
#                     readIO_size=x[27],
#                     writeIO_size=x[28],
#                     readdisk_time=x[29],
#                     writedisk_time=x[30],
#                     nic1_datasent_size=x[31],
#                     nic1_datasent_num=x[32],
#                     nic1_datareceived_size=x[33],
#                     nic1_datareceived_num=x[34],
#                     nic1_datareceived_error=x[35],
#                     nic1_datasent_error=x[36]
#                 )
#         elif internum == 2:
#             h1 = df1.columns.tolist()
#             mysysteminfo.objects.create(
#                 timestamp=h1[0],
#                 CPUlogics_num=h1[1],
#                 CPUphysicals_num=h1[2],
#                 CPU_usage=h1[3],
#                 CPU_freq=h1[4],
#                 UserMode_runtime=h1[5],
#                 CoreState_runtime=h1[6],
#                 IOwait_time=h1[7],
#                 Averload_in1min=h1[8],
#                 Averload_in5min=h1[9],
#                 Averload_in15min=h1[10],
#                 interruptions_num=h1[11],
#                 softinterruptions_num=h1[12],
#                 systemcalls_num=h1[13],
#
#                 Totalmemory_size=h1[14],
#                 Usedmemory_size=h1[15],
#                 Freememory_size=h1[16],
#                 Memory_usage=h1[17],
#                 Swapmemory_size=h1[18],
#                 UsedSwapmemory_size=h1[19],
#                 FreeSwapmemory_size=h1[20],
#                 Swapmemory_usage=h1[21],
#
#                 Totaldisk_size=h1[22],
#                 Useddisk_size=h1[23],
#                 Freedisk_size=h1[24],
#                 Disk_usage=h1[25],
#                 readIO_size=h1[26],
#                 writeIO_size=h1[27],
#                 readdisk_time=h1[28],
#                 writedisk_time=h1[29],
#                 nic1_datasent_size=h1[30],
#                 nic1_datasent_num=h1[31],
#                 nic1_datareceived_size=h1[32],
#                 nic1_datareceived_num=h1[33],
#                 nic1_datareceived_error=h1[34],
#                 nic1_datasent_error=h1[35],
#                 nic2_datasent_size=h1[36],
#                 nic2_datasent_num=h1[37],
#                 nic2_datareceived_size=h1[38],
#                 nic2_datareceived_num=h1[39],
#                 nic2_datareceived_error=h1[40],
#                 nic2_datasent_error=h1[41]
#
#
#             )
#             for x in df1.itertuples():
#                 mysysteminfo.objects.create(
#                     timestamp=x[1],
#                     CPUlogics_num=x[2],
#                     CPUphysicals_num=x[3],
#                     CPU_usage=x[4],
#                     CPU_freq=x[5],
#                     UserMode_runtime=x[6],
#                     CoreState_runtime=x[7],
#                     IOwait_time=x[8],
#                     Averload_in1min=x[9],
#                     Averload_in5min=x[10],
#                     Averload_in15min=x[11],
#                     interruptions_num=x[12],
#                     softinterruptions_num=x[13],
#                     systemcalls_num=x[14],
#
#                     Totalmemory_size=x[15],
#                     Usedmemory_size=x[16],
#                     Freememory_size=x[17],
#                     Memory_usage=x[18],
#                     Swapmemory_size=x[19],
#                     UsedSwapmemory_size=x[20],
#                     FreeSwapmemory_size=x[21],
#                     Swapmemory_usage=x[22],
#
#                     Totaldisk_size=x[23],
#                     Useddisk_size=x[24],
#                     Freedisk_size=x[25],
#                     Disk_usage=x[26],
#                     readIO_size=x[27],
#                     writeIO_size=x[28],
#                     readdisk_time=x[29],
#                     writedisk_time=x[30],
#                     nic1_datasent_size=x[31],
#                     nic1_datasent_num=x[32],
#                     nic1_datareceived_size=x[33],
#                     nic1_datareceived_num=x[34],
#                     nic1_datareceived_error=x[35],
#                     nic1_datasent_error=x[36],
#                     nic2_datasent_size=x[37],
#                     nic2_datasent_num=x[38],
#                     nic2_datareceived_size=x[39],
#                     nic2_datareceived_num=x[40],
#                     nic2_datareceived_error=x[41],
#                     nic2_datasent_error=x[42]
#
#                 )
#         elif internum == 3:
#             h1 = df1.columns.tolist()
#             mysysteminfo.objects.create(
#                 timestamp=h1[0],
#                 CPUlogics_num=h1[1],
#                 CPUphysicals_num=h1[2],
#                 CPU_usage=h1[3],
#                 CPU_freq=h1[4],
#                 UserMode_runtime=h1[5],
#                 CoreState_runtime=h1[6],
#                 IOwait_time=h1[7],
#                 Averload_in1min=h1[8],
#                 Averload_in5min=h1[9],
#                 Averload_in15min=h1[10],
#                 interruptions_num=h1[11],
#                 softinterruptions_num=h1[12],
#                 systemcalls_num=h1[13],
#
#                 Totalmemory_size=h1[14],
#                 Usedmemory_size=h1[15],
#                 Freememory_size=h1[16],
#                 Memory_usage=h1[17],
#                 Swapmemory_size=h1[18],
#                 UsedSwapmemory_size=h1[19],
#                 FreeSwapmemory_size=h1[20],
#                 Swapmemory_usage=h1[21],
#
#                 Totaldisk_size=h1[22],
#                 Useddisk_size=h1[23],
#                 Freedisk_size=h1[24],
#                 Disk_usage=h1[25],
#                 readIO_size=h1[26],
#                 writeIO_size=h1[27],
#                 readdisk_time=h1[28],
#                 writedisk_time=h1[29],
#                 nic1_datasent_size=h1[30],
#                 nic1_datasent_num=h1[31],
#                 nic1_datareceived_size=h1[32],
#                 nic1_datareceived_num=h1[33],
#                 nic1_datareceived_error=h1[34],
#                 nic1_datasent_error=h1[35],
#                 nic2_datasent_size=h1[36],
#                 nic2_datasent_num=h1[37],
#                 nic2_datareceived_size=h1[38],
#                 nic2_datareceived_num=h1[39],
#                 nic2_datareceived_error=h1[40],
#                 nic2_datasent_error=h1[41],
#                 nic3_datasent_size=h1[42],
#                 nic3_datasent_num=h1[43],
#                 nic3_datareceived_size=h1[44],
#                 nic3_datareceived_num=h1[45],
#                 nic3_datareceived_error=h1[46],
#                 nic3_datasent_error=h1[47]
#
#
#             )
#             for x in df1.itertuples():
#                 mysysteminfo.objects.create(
#                     timestamp=x[1],
#                     CPUlogics_num=x[2],
#                     CPUphysicals_num=x[3],
#                     CPU_usage=x[4],
#                     CPU_freq=x[5],
#                     UserMode_runtime=x[6],
#                     CoreState_runtime=x[7],
#                     IOwait_time=x[8],
#                     Averload_in1min=x[9],
#                     Averload_in5min=x[10],
#                     Averload_in15min=x[11],
#                     interruptions_num=x[12],
#                     softinterruptions_num=x[13],
#                     systemcalls_num=x[14],
#
#                     Totalmemory_size=x[15],
#                     Usedmemory_size=x[16],
#                     Freememory_size=x[17],
#                     Memory_usage=x[18],
#                     Swapmemory_size=x[19],
#                     UsedSwapmemory_size=x[20],
#                     FreeSwapmemory_size=x[21],
#                     Swapmemory_usage=x[22],
#
#                     Totaldisk_size=x[23],
#                     Useddisk_size=x[24],
#                     Freedisk_size=x[25],
#                     Disk_usage=x[26],
#                     readIO_size=x[27],
#                     writeIO_size=x[28],
#                     readdisk_time=x[29],
#                     writedisk_time=x[30],
#                     nic1_datasent_size=x[31],
#                     nic1_datasent_num=x[32],
#                     nic1_datareceived_size=x[33],
#                     nic1_datareceived_num=x[34],
#                     nic1_datareceived_error=x[35],
#                     nic1_datasent_error=x[36],
#                     nic2_datasent_size=x[37],
#                     nic2_datasent_num=x[38],
#                     nic2_datareceived_size=x[39],
#                     nic2_datareceived_num=x[40],
#                     nic2_datareceived_error=x[41],
#                     nic2_datasent_error=x[42],
#                     nic3_datasent_size=x[43],
#                     nic3_datasent_num=x[44],
#                     nic3_datareceived_size=x[45],
#                     nic3_datareceived_num=x[46],
#                     nic3_datareceived_error=x[47],
#                     nic3_datasent_error=x[48]
#                 )
#         elif internum == 4:
#             h1 = df1.columns.tolist()
#             mysysteminfo.objects.create(
#                 timestamp=h1[0],
#                 CPUlogics_num=h1[1],
#                 CPUphysicals_num=h1[2],
#                 CPU_usage=h1[3],
#                 CPU_freq=h1[4],
#                 UserMode_runtime=h1[5],
#                 CoreState_runtime=h1[6],
#                 IOwait_time=h1[7],
#                 Averload_in1min=h1[8],
#                 Averload_in5min=h1[9],
#                 Averload_in15min=h1[10],
#                 interruptions_num=h1[11],
#                 softinterruptions_num=h1[12],
#                 systemcalls_num=h1[13],
#
#                 Totalmemory_size=h1[14],
#                 Usedmemory_size=h1[15],
#                 Freememory_size=h1[16],
#                 Memory_usage=h1[17],
#                 Swapmemory_size=h1[18],
#                 UsedSwapmemory_size=h1[19],
#                 FreeSwapmemory_size=h1[20],
#                 Swapmemory_usage=h1[21],
#
#                 Totaldisk_size=h1[22],
#                 Useddisk_size=h1[23],
#                 Freedisk_size=h1[24],
#                 Disk_usage=h1[25],
#                 readIO_size=h1[26],
#                 writeIO_size=h1[27],
#                 readdisk_time=h1[28],
#                 writedisk_time=h1[29],
#                 nic1_datasent_size=h1[30],
#                 nic1_datasent_num=h1[31],
#                 nic1_datareceived_size=h1[32],
#                 nic1_datareceived_num=h1[33],
#                 nic1_datareceived_error=h1[34],
#                 nic1_datasent_error=h1[35],
#                 nic2_datasent_size=h1[36],
#                 nic2_datasent_num=h1[37],
#                 nic2_datareceived_size=h1[38],
#                 nic2_datareceived_num=h1[39],
#                 nic2_datareceived_error=h1[40],
#                 nic2_datasent_error=h1[41],
#                 nic3_datasent_size=h1[42],
#                 nic3_datasent_num=h1[43],
#                 nic3_datareceived_size=h1[44],
#                 nic3_datareceived_num=h1[45],
#                 nic3_datareceived_error=h1[46],
#                 nic3_datasent_error=h1[47],
#                 nic4_datasent_size=h1[48],
#                 nic4_datasent_num=h1[49],
#                 nic4_datareceived_size=h1[50],
#                 nic4_datareceived_num=h1[51],
#                 nic4_datareceived_error=h1[52],
#                 nic4_datasent_error=h1[53]
#
#
#             )
#             for x in df1.itertuples():
#                 mysysteminfo.objects.create(
#                     timestamp=x[1],
#                     CPUlogics_num=x[2],
#                     CPUphysicals_num=x[3],
#                     CPU_usage=x[4],
#                     CPU_freq=x[5],
#                     UserMode_runtime=x[6],
#                     CoreState_runtime=x[7],
#                     IOwait_time=x[8],
#                     Averload_in1min=x[9],
#                     Averload_in5min=x[10],
#                     Averload_in15min=x[11],
#                     interruptions_num=x[12],
#                     softinterruptions_num=x[13],
#                     systemcalls_num=x[14],
#
#                     Totalmemory_size=x[15],
#                     Usedmemory_size=x[16],
#                     Freememory_size=x[17],
#                     Memory_usage=x[18],
#                     Swapmemory_size=x[19],
#                     UsedSwapmemory_size=x[20],
#                     FreeSwapmemory_size=x[21],
#                     Swapmemory_usage=x[22],
#
#                     Totaldisk_size=x[23],
#                     Useddisk_size=x[24],
#                     Freedisk_size=x[25],
#                     Disk_usage=x[26],
#                     readIO_size=x[27],
#                     writeIO_size=x[28],
#                     readdisk_time=x[29],
#                     writedisk_time=x[30],
#                     nic1_datasent_size=x[31],
#                     nic1_datasent_num=x[32],
#                     nic1_datareceived_size=x[33],
#                     nic1_datareceived_num=x[34],
#                     nic1_datareceived_error=x[35],
#                     nic1_datasent_error=x[36],
#                     nic2_datasent_size=x[37],
#                     nic2_datasent_num=x[38],
#                     nic2_datareceived_size=x[39],
#                     nic2_datareceived_num=x[40],
#                     nic2_datareceived_error=x[41],
#                     nic2_datasent_error=x[42],
#                     nic3_datasent_size=x[43],
#                     nic3_datasent_num=x[44],
#                     nic3_datareceived_size=x[45],
#                     nic3_datareceived_num=x[46],
#                     nic3_datareceived_error=x[47],
#                     nic3_datasent_error=x[48],
#                     nic4_datasent_size=x[49],
#                     nic4_datasent_num=x[50],
#                     nic4_datareceived_size=x[51],
#                     nic4_datareceived_num=x[52],
#                     nic4_datareceived_error=x[53],
#                     nic4_datasent_error=x[54]
#                 )
#         elif internum == 5:
#             h1 = df1.columns.tolist()
#             mysysteminfo.objects.create(
#                 timestamp=h1[0],
#                 CPUlogics_num=h1[1],
#                 CPUphysicals_num=h1[2],
#                 CPU_usage=h1[3],
#                 CPU_freq=h1[4],
#                 UserMode_runtime=h1[5],
#                 CoreState_runtime=h1[6],
#                 IOwait_time=h1[7],
#                 Averload_in1min=h1[8],
#                 Averload_in5min=h1[9],
#                 Averload_in15min=h1[10],
#                 interruptions_num=h1[11],
#                 softinterruptions_num=h1[12],
#                 systemcalls_num=h1[13],
#
#                 Totalmemory_size=h1[14],
#                 Usedmemory_size=h1[15],
#                 Freememory_size=h1[16],
#                 Memory_usage=h1[17],
#                 Swapmemory_size=h1[18],
#                 UsedSwapmemory_size=h1[19],
#                 FreeSwapmemory_size=h1[20],
#                 Swapmemory_usage=h1[21],
#
#                 Totaldisk_size=h1[22],
#                 Useddisk_size=h1[23],
#                 Freedisk_size=h1[24],
#                 Disk_usage=h1[25],
#                 readIO_size=h1[26],
#                 writeIO_size=h1[27],
#                 readdisk_time=h1[28],
#                 writedisk_time=h1[29],
#                 nic1_datasent_size=h1[30],
#                 nic1_datasent_num=h1[31],
#                 nic1_datareceived_size=h1[32],
#                 nic1_datareceived_num=h1[33],
#                 nic1_datareceived_error=h1[34],
#                 nic1_datasent_error=h1[35],
#                 nic2_datasent_size=h1[36],
#                 nic2_datasent_num=h1[37],
#                 nic2_datareceived_size=h1[38],
#                 nic2_datareceived_num=h1[39],
#                 nic2_datareceived_error=h1[40],
#                 nic2_datasent_error=h1[41],
#                 nic3_datasent_size=h1[42],
#                 nic3_datasent_num=h1[43],
#                 nic3_datareceived_size=h1[44],
#                 nic3_datareceived_num=h1[45],
#                 nic3_datareceived_error=h1[46],
#                 nic3_datasent_error=h1[47],
#                 nic4_datasent_size=h1[48],
#                 nic4_datasent_num=h1[49],
#                 nic4_datareceived_size=h1[50],
#                 nic4_datareceived_num=h1[51],
#                 nic4_datareceived_error=h1[52],
#                 nic4_datasent_error=h1[53],
#                 nic5_datasent_size=h1[54],
#                 nic5_datasent_num=h1[55],
#                 nic5_datareceived_size=h1[56],
#                 nic5_datareceived_num=h1[57],
#                 nic5_datareceived_error=h1[58],
#                 nic5_datasent_error=h1[59]
#
#
#             )
#             for x in df1.itertuples():
#                 mysysteminfo.objects.create(
#                     timestamp=x[1],
#                     CPUlogics_num=x[2],
#                     CPUphysicals_num=x[3],
#                     CPU_usage=x[4],
#                     CPU_freq=x[5],
#                     UserMode_runtime=x[6],
#                     CoreState_runtime=x[7],
#                     IOwait_time=x[8],
#                     Averload_in1min=x[9],
#                     Averload_in5min=x[10],
#                     Averload_in15min=x[11],
#                     interruptions_num=x[12],
#                     softinterruptions_num=x[13],
#                     systemcalls_num=x[14],
#
#                     Totalmemory_size=x[15],
#                     Usedmemory_size=x[16],
#                     Freememory_size=x[17],
#                     Memory_usage=x[18],
#                     Swapmemory_size=x[19],
#                     UsedSwapmemory_size=x[20],
#                     FreeSwapmemory_size=x[21],
#                     Swapmemory_usage=x[22],
#
#                     Totaldisk_size=x[23],
#                     Useddisk_size=x[24],
#                     Freedisk_size=x[25],
#                     Disk_usage=x[26],
#                     readIO_size=x[27],
#                     writeIO_size=x[28],
#                     readdisk_time=x[29],
#                     writedisk_time=x[30],
#                     nic1_datasent_size=x[31],
#                     nic1_datasent_num=x[32],
#                     nic1_datareceived_size=x[33],
#                     nic1_datareceived_num=x[34],
#                     nic1_datareceived_error=x[35],
#                     nic1_datasent_error=x[36],
#                     nic2_datasent_size=x[37],
#                     nic2_datasent_num=x[38],
#                     nic2_datareceived_size=x[39],
#                     nic2_datareceived_num=x[40],
#                     nic2_datareceived_error=x[41],
#                     nic2_datasent_error=x[42],
#                     nic3_datasent_size=x[43],
#                     nic3_datasent_num=x[44],
#                     nic3_datareceived_size=x[45],
#                     nic3_datareceived_num=x[46],
#                     nic3_datareceived_error=x[47],
#                     nic3_datasent_error=x[48],
#                     nic4_datasent_size=x[49],
#                     nic4_datasent_num=x[50],
#                     nic4_datareceived_size=x[51],
#                     nic4_datareceived_num=x[52],
#                     nic4_datareceived_error=x[53],
#                     nic4_datasent_error=x[54],
#                     nic5_datasent_size=x[55],
#                     nic5_datasent_num=x[56],
#                     nic5_datareceived_size=x[57],
#                     nic5_datareceived_num=x[58],
#                     nic5_datareceived_error=x[59],
#                     nic5_datasent_error=x[60]
#
#
#                 )
#         elif internum == 6:
#             h1 = df1.columns.tolist()
#             mysysteminfo.objects.create(
#                 timestamp=h1[0],
#                 CPUlogics_num=h1[1],
#                 CPUphysicals_num=h1[2],
#                 CPU_usage=h1[3],
#                 CPU_freq=h1[4],
#                 UserMode_runtime=h1[5],
#                 CoreState_runtime=h1[6],
#                 IOwait_time=h1[7],
#                 Averload_in1min=h1[8],
#                 Averload_in5min=h1[9],
#                 Averload_in15min=h1[10],
#                 interruptions_num=h1[11],
#                 softinterruptions_num=h1[12],
#                 systemcalls_num=h1[13],
#
#                 Totalmemory_size=h1[14],
#                 Usedmemory_size=h1[15],
#                 Freememory_size=h1[16],
#                 Memory_usage=h1[17],
#                 Swapmemory_size=h1[18],
#                 UsedSwapmemory_size=h1[19],
#                 FreeSwapmemory_size=h1[20],
#                 Swapmemory_usage=h1[21],
#
#                 Totaldisk_size=h1[22],
#                 Useddisk_size=h1[23],
#                 Freedisk_size=h1[24],
#                 Disk_usage=h1[25],
#                 readIO_size=h1[26],
#                 writeIO_size=h1[27],
#                 readdisk_time=h1[28],
#                 writedisk_time=h1[29],
#                 nic1_datasent_size=h1[30],
#                 nic1_datasent_num=h1[31],
#                 nic1_datareceived_size=h1[32],
#                 nic1_datareceived_num=h1[33],
#                 nic1_datareceived_error=h1[34],
#                 nic1_datasent_error=h1[35],
#                 nic2_datasent_size=h1[36],
#                 nic2_datasent_num=h1[37],
#                 nic2_datareceived_size=h1[38],
#                 nic2_datareceived_num=h1[39],
#                 nic2_datareceived_error=h1[40],
#                 nic2_datasent_error=h1[41],
#                 nic3_datasent_size=h1[42],
#                 nic3_datasent_num=h1[43],
#                 nic3_datareceived_size=h1[44],
#                 nic3_datareceived_num=h1[45],
#                 nic3_datareceived_error=h1[46],
#                 nic3_datasent_error=h1[47],
#                 nic4_datasent_size=h1[48],
#                 nic4_datasent_num=h1[49],
#                 nic4_datareceived_size=h1[50],
#                 nic4_datareceived_num=h1[51],
#                 nic4_datareceived_error=h1[52],
#                 nic4_datasent_error=h1[53],
#                 nic5_datasent_size=h1[54],
#                 nic5_datasent_num=h1[55],
#                 nic5_datareceived_size=h1[56],
#                 nic5_datareceived_num=h1[57],
#                 nic5_datareceived_error=h1[58],
#                 nic5_datasent_error=h1[59],
#                 nic6_datasent_size=h1[60],
#                 nic6_datasent_num=h1[61],
#                 nic6_datareceived_size=h1[62],
#                 nic6_datareceived_num=h1[63],
#                 nic6_datareceived_error=h1[64],
#                 nic6_datasent_error=h1[65]
#             )
#             for x in df1.itertuples():
#                 mysysteminfo.objects.create(
#                     timestamp=x[1],
#                     CPUlogics_num=x[2],
#                     CPUphysicals_num=x[3],
#                     CPU_usage=x[4],
#                     CPU_freq=x[5],
#                     UserMode_runtime=x[6],
#                     CoreState_runtime=x[7],
#                     IOwait_time=x[8],
#                     Averload_in1min=x[9],
#                     Averload_in5min=x[10],
#                     Averload_in15min=x[11],
#                     interruptions_num=x[12],
#                     softinterruptions_num=x[13],
#                     systemcalls_num=x[14],
#
#                     Totalmemory_size=x[15],
#                     Usedmemory_size=x[16],
#                     Freememory_size=x[17],
#                     Memory_usage=x[18],
#                     Swapmemory_size=x[19],
#                     UsedSwapmemory_size=x[20],
#                     FreeSwapmemory_size=x[21],
#                     Swapmemory_usage=x[22],
#
#                     Totaldisk_size=x[23],
#                     Useddisk_size=x[24],
#                     Freedisk_size=x[25],
#                     Disk_usage=x[26],
#                     readIO_size=x[27],
#                     writeIO_size=x[28],
#                     readdisk_time=x[29],
#                     writedisk_time=x[30],
#                     nic1_datasent_size=x[31],
#                     nic1_datasent_num=x[32],
#                     nic1_datareceived_size=x[33],
#                     nic1_datareceived_num=x[34],
#                     nic1_datareceived_error=x[35],
#                     nic1_datasent_error=x[36],
#                     nic2_datasent_size=x[37],
#                     nic2_datasent_num=x[38],
#                     nic2_datareceived_size=x[39],
#                     nic2_datareceived_num=x[40],
#                     nic2_datareceived_error=x[41],
#                     nic2_datasent_error=x[42],
#                     nic3_datasent_size=x[43],
#                     nic3_datasent_num=x[44],
#                     nic3_datareceived_size=x[45],
#                     nic3_datareceived_num=x[46],
#                     nic3_datareceived_error=x[47],
#                     nic3_datasent_error=x[48],
#                     nic4_datasent_size=x[49],
#                     nic4_datasent_num=x[50],
#                     nic4_datareceived_size=x[51],
#                     nic4_datareceived_num=x[52],
#                     nic4_datareceived_error=x[53],
#                     nic4_datasent_error=x[54],
#                     nic5_datasent_size=x[55],
#                     nic5_datasent_num=x[56],
#                     nic5_datareceived_size=x[57],
#                     nic5_datareceived_num=x[58],
#                     nic5_datareceived_error=x[59],
#                     nic5_datasent_error=x[60],
#                     nic6_datasent_size=x[61],
#                     nic6_datasent_num=x[62],
#                     nic6_datareceived_size=x[63],
#                     nic6_datareceived_num=x[64],
#                     nic6_datareceived_error=x[65],
#                     nic6_datasent_error=x[66]
#
#
#                 )
#         elif internum == 7:
#             h1 = df1.columns.tolist()
#             mysysteminfo.objects.create(
#                 timestamp=h1[0],
#                 CPUlogics_num=h1[1],
#                 CPUphysicals_num=h1[2],
#                 CPU_usage=h1[3],
#                 CPU_freq=h1[4],
#                 UserMode_runtime=h1[5],
#                 CoreState_runtime=h1[6],
#                 IOwait_time=h1[7],
#                 Averload_in1min=h1[8],
#                 Averload_in5min=h1[9],
#                 Averload_in15min=h1[10],
#                 interruptions_num=h1[11],
#                 softinterruptions_num=h1[12],
#                 systemcalls_num=h1[13],
#
#                 Totalmemory_size=h1[14],
#                 Usedmemory_size=h1[15],
#                 Freememory_size=h1[16],
#                 Memory_usage=h1[17],
#                 Swapmemory_size=h1[18],
#                 UsedSwapmemory_size=h1[19],
#                 FreeSwapmemory_size=h1[20],
#                 Swapmemory_usage=h1[21],
#
#                 Totaldisk_size=h1[22],
#                 Useddisk_size=h1[23],
#                 Freedisk_size=h1[24],
#                 Disk_usage=h1[25],
#                 readIO_size=h1[26],
#                 writeIO_size=h1[27],
#                 readdisk_time=h1[28],
#                 writedisk_time=h1[29],
#                 nic1_datasent_size=h1[30],
#                 nic1_datasent_num=h1[31],
#                 nic1_datareceived_size=h1[32],
#                 nic1_datareceived_num=h1[33],
#                 nic1_datareceived_error=h1[34],
#                 nic1_datasent_error=h1[35],
#                 nic2_datasent_size=h1[36],
#                 nic2_datasent_num=h1[37],
#                 nic2_datareceived_size=h1[38],
#                 nic2_datareceived_num=h1[39],
#                 nic2_datareceived_error=h1[40],
#                 nic2_datasent_error=h1[41],
#                 nic3_datasent_size=h1[42],
#                 nic3_datasent_num=h1[43],
#                 nic3_datareceived_size=h1[44],
#                 nic3_datareceived_num=h1[45],
#                 nic3_datareceived_error=h1[46],
#                 nic3_datasent_error=h1[47],
#                 nic4_datasent_size=h1[48],
#                 nic4_datasent_num=h1[49],
#                 nic4_datareceived_size=h1[50],
#                 nic4_datareceived_num=h1[51],
#                 nic4_datareceived_error=h1[52],
#                 nic4_datasent_error=h1[53],
#                 nic5_datasent_size=h1[54],
#                 nic5_datasent_num=h1[55],
#                 nic5_datareceived_size=h1[56],
#                 nic5_datareceived_num=h1[57],
#                 nic5_datareceived_error=h1[58],
#                 nic5_datasent_error=h1[59],
#                 nic6_datasent_size=h1[60],
#                 nic6_datasent_num=h1[61],
#                 nic6_datareceived_size=h1[62],
#                 nic6_datareceived_num=h1[63],
#                 nic6_datareceived_error=h1[64],
#                 nic6_datasent_error=h1[65],
#                 nic7_datasent_size=h1[66],
#                 nic7_datasent_num=h1[67],
#                 nic7_datareceived_size=h1[68],
#                 nic7_datareceived_num=h1[69],
#                 nic7_datareceived_error=h1[70],
#                 nic7_datasent_error=h1[71]
#
#
#             )
#             for x in df1.itertuples():
#                 mysysteminfo.objects.create(
#                     timestamp=x[1],
#                     CPUlogics_num=x[2],
#                     CPUphysicals_num=x[3],
#                     CPU_usage=x[4],
#                     CPU_freq=x[5],
#                     UserMode_runtime=x[6],
#                     CoreState_runtime=x[7],
#                     IOwait_time=x[8],
#                     Averload_in1min=x[9],
#                     Averload_in5min=x[10],
#                     Averload_in15min=x[11],
#                     interruptions_num=x[12],
#                     softinterruptions_num=x[13],
#                     systemcalls_num=x[14],
#
#                     Totalmemory_size=x[15],
#                     Usedmemory_size=x[16],
#                     Freememory_size=x[17],
#                     Memory_usage=x[18],
#                     Swapmemory_size=x[19],
#                     UsedSwapmemory_size=x[20],
#                     FreeSwapmemory_size=x[21],
#                     Swapmemory_usage=x[22],
#
#                     Totaldisk_size=x[23],
#                     Useddisk_size=x[24],
#                     Freedisk_size=x[25],
#                     Disk_usage=x[26],
#                     readIO_size=x[27],
#                     writeIO_size=x[28],
#                     readdisk_time=x[29],
#                     writedisk_time=x[30],
#                     nic1_datasent_size=x[31],
#                     nic1_datasent_num=x[32],
#                     nic1_datareceived_size=x[33],
#                     nic1_datareceived_num=x[34],
#                     nic1_datareceived_error=x[35],
#                     nic1_datasent_error=x[36],
#                     nic2_datasent_size=x[37],
#                     nic2_datasent_num=x[38],
#                     nic2_datareceived_size=x[39],
#                     nic2_datareceived_num=x[40],
#                     nic2_datareceived_error=x[41],
#                     nic2_datasent_error=x[42],
#                     nic3_datasent_size=x[43],
#                     nic3_datasent_num=x[44],
#                     nic3_datareceived_size=x[45],
#                     nic3_datareceived_num=x[46],
#                     nic3_datareceived_error=x[47],
#                     nic3_datasent_error=x[48],
#                     nic4_datasent_size=x[49],
#                     nic4_datasent_num=x[50],
#                     nic4_datareceived_size=x[51],
#                     nic4_datareceived_num=x[52],
#                     nic4_datareceived_error=x[53],
#                     nic4_datasent_error=x[54],
#                     nic5_datasent_size=x[55],
#                     nic5_datasent_num=x[56],
#                     nic5_datareceived_size=x[57],
#                     nic5_datareceived_num=x[58],
#                     nic5_datareceived_error=x[59],
#                     nic5_datasent_error=x[60],
#                     nic6_datasent_size=x[61],
#                     nic6_datasent_num=x[62],
#                     nic6_datareceived_size=x[63],
#                     nic6_datareceived_num=x[64],
#                     nic6_datareceived_error=x[65],
#                     nic6_datasent_error=x[66],
#                     nic7_datasent_size=x[67],
#                     nic7_datasent_num=x[68],
#                     nic7_datareceived_size=x[69],
#                     nic7_datareceived_num=x[70],
#                     nic7_datareceived_error=x[71],
#                     nic7_datasent_error=x[72]
#
#
#                 )
#         elif internum == 8:
#             h1 = df1.columns.tolist()
#             mysysteminfo.objects.create(
#                 timestamp=h1[0],
#                 CPUlogics_num=h1[1],
#                 CPUphysicals_num=h1[2],
#                 CPU_usage=h1[3],
#                 CPU_freq=h1[4],
#                 UserMode_runtime=h1[5],
#                 CoreState_runtime=h1[6],
#                 IOwait_time=h1[7],
#                 Averload_in1min=h1[8],
#                 Averload_in5min=h1[9],
#                 Averload_in15min=h1[10],
#                 interruptions_num=h1[11],
#                 softinterruptions_num=h1[12],
#                 systemcalls_num=h1[13],
#
#                 Totalmemory_size=h1[14],
#                 Usedmemory_size=h1[15],
#                 Freememory_size=h1[16],
#                 Memory_usage=h1[17],
#                 Swapmemory_size=h1[18],
#                 UsedSwapmemory_size=h1[19],
#                 FreeSwapmemory_size=h1[20],
#                 Swapmemory_usage=h1[21],
#
#                 Totaldisk_size=h1[22],
#                 Useddisk_size=h1[23],
#                 Freedisk_size=h1[24],
#                 Disk_usage=h1[25],
#                 readIO_size=h1[26],
#                 writeIO_size=h1[27],
#                 readdisk_time=h1[28],
#                 writedisk_time=h1[29],
#                 nic1_datasent_size=h1[30],
#                 nic1_datasent_num=h1[31],
#                 nic1_datareceived_size=h1[32],
#                 nic1_datareceived_num=h1[33],
#                 nic1_datareceived_error=h1[34],
#                 nic1_datasent_error=h1[35],
#                 nic2_datasent_size=h1[36],
#                 nic2_datasent_num=h1[37],
#                 nic2_datareceived_size=h1[38],
#                 nic2_datareceived_num=h1[39],
#                 nic2_datareceived_error=h1[40],
#                 nic2_datasent_error=h1[41],
#                 nic3_datasent_size=h1[42],
#                 nic3_datasent_num=h1[43],
#                 nic3_datareceived_size=h1[44],
#                 nic3_datareceived_num=h1[45],
#                 nic3_datareceived_error=h1[46],
#                 nic3_datasent_error=h1[47],
#                 nic4_datasent_size=h1[48],
#                 nic4_datasent_num=h1[49],
#                 nic4_datareceived_size=h1[50],
#                 nic4_datareceived_num=h1[51],
#                 nic4_datareceived_error=h1[52],
#                 nic4_datasent_error=h1[53],
#                 nic5_datasent_size=h1[54],
#                 nic5_datasent_num=h1[55],
#                 nic5_datareceived_size=h1[56],
#                 nic5_datareceived_num=h1[57],
#                 nic5_datareceived_error=h1[58],
#                 nic5_datasent_error=h1[59],
#                 nic6_datasent_size=h1[60],
#                 nic6_datasent_num=h1[61],
#                 nic6_datareceived_size=h1[62],
#                 nic6_datareceived_num=h1[63],
#                 nic6_datareceived_error=h1[64],
#                 nic6_datasent_error=h1[65],
#                 nic7_datasent_size=h1[66],
#                 nic7_datasent_num=h1[67],
#                 nic7_datareceived_size=h1[68],
#                 nic7_datareceived_num=h1[69],
#                 nic7_datareceived_error=h1[70],
#                 nic7_datasent_error=h1[71],
#                 nic8_datasent_size=h1[72],
#                 nic8_datasent_num=h1[73],
#                 nic8_datareceived_size=h1[74],
#                 nic8_datareceived_num=h1[75],
#                 nic8_datareceived_error=h1[76],
#                 nic8_datasent_error=h1[77]
#
#
#             )
#             for x in df1.itertuples():
#                 mysysteminfo.objects.create(
#                     timestamp=x[1],
#                     CPUlogics_num=x[2],
#                     CPUphysicals_num=x[3],
#                     CPU_usage=x[4],
#                     CPU_freq=x[5],
#                     UserMode_runtime=x[6],
#                     CoreState_runtime=x[7],
#                     IOwait_time=x[8],
#                     Averload_in1min=x[9],
#                     Averload_in5min=x[10],
#                     Averload_in15min=x[11],
#                     interruptions_num=x[12],
#                     softinterruptions_num=x[13],
#                     systemcalls_num=x[14],
#
#                     Totalmemory_size=x[15],
#                     Usedmemory_size=x[16],
#                     Freememory_size=x[17],
#                     Memory_usage=x[18],
#                     Swapmemory_size=x[19],
#                     UsedSwapmemory_size=x[20],
#                     FreeSwapmemory_size=x[21],
#                     Swapmemory_usage=x[22],
#
#                     Totaldisk_size=x[23],
#                     Useddisk_size=x[24],
#                     Freedisk_size=x[25],
#                     Disk_usage=x[26],
#                     readIO_size=x[27],
#                     writeIO_size=x[28],
#                     readdisk_time=x[29],
#                     writedisk_time=x[30],
#                     nic1_datasent_size=x[31],
#                     nic1_datasent_num=x[32],
#                     nic1_datareceived_size=x[33],
#                     nic1_datareceived_num=x[34],
#                     nic1_datareceived_error=x[35],
#                     nic1_datasent_error=x[36],
#                     nic2_datasent_size=x[37],
#                     nic2_datasent_num=x[38],
#                     nic2_datareceived_size=x[39],
#                     nic2_datareceived_num=x[40],
#                     nic2_datareceived_error=x[41],
#                     nic2_datasent_error=x[42],
#                     nic3_datasent_size=x[43],
#                     nic3_datasent_num=x[44],
#                     nic3_datareceived_size=x[45],
#                     nic3_datareceived_num=x[46],
#                     nic3_datareceived_error=x[47],
#                     nic3_datasent_error=x[48],
#                     nic4_datasent_size=x[49],
#                     nic4_datasent_num=x[50],
#                     nic4_datareceived_size=x[51],
#                     nic4_datareceived_num=x[52],
#                     nic4_datareceived_error=x[53],
#                     nic4_datasent_error=x[54],
#                     nic5_datasent_size=x[55],
#                     nic5_datasent_num=x[56],
#                     nic5_datareceived_size=x[57],
#                     nic5_datareceived_num=x[58],
#                     nic5_datareceived_error=x[59],
#                     nic5_datasent_error=x[60],
#                     nic6_datasent_size=x[61],
#                     nic6_datasent_num=x[62],
#                     nic6_datareceived_size=x[63],
#                     nic6_datareceived_num=x[64],
#                     nic6_datareceived_error=x[65],
#                     nic6_datasent_error=x[66],
#                     nic7_datasent_size=x[67],
#                     nic7_datasent_num=x[68],
#                     nic7_datareceived_size=x[69],
#                     nic7_datareceived_num=x[70],
#                     nic7_datareceived_error=x[71],
#                     nic7_datasent_error=x[72],
#                     nic8_datasent_size=x[73],
#                     nic8_datasent_num=x[74],
#                     nic8_datareceived_size=x[75],
#                     nic8_datareceived_num=x[76],
#                     nic8_datareceived_error=x[77],
#                     nic8_datasent_error=x[78]
#
#
#                 )
#         elif internum == 9:
#             h1 = df1.columns.tolist()
#             mysysteminfo.objects.create(
#                 timestamp=h1[0],
#                 CPUlogics_num=h1[1],
#                 CPUphysicals_num=h1[2],
#                 CPU_usage=h1[3],
#                 CPU_freq=h1[4],
#                 UserMode_runtime=h1[5],
#                 CoreState_runtime=h1[6],
#                 IOwait_time=h1[7],
#                 Averload_in1min=h1[8],
#                 Averload_in5min=h1[9],
#                 Averload_in15min=h1[10],
#                 interruptions_num=h1[11],
#                 softinterruptions_num=h1[12],
#                 systemcalls_num=h1[13],
#
#                 Totalmemory_size=h1[14],
#                 Usedmemory_size=h1[15],
#                 Freememory_size=h1[16],
#                 Memory_usage=h1[17],
#                 Swapmemory_size=h1[18],
#                 UsedSwapmemory_size=h1[19],
#                 FreeSwapmemory_size=h1[20],
#                 Swapmemory_usage=h1[21],
#
#                 Totaldisk_size=h1[22],
#                 Useddisk_size=h1[23],
#                 Freedisk_size=h1[24],
#                 Disk_usage=h1[25],
#                 readIO_size=h1[26],
#                 writeIO_size=h1[27],
#                 readdisk_time=h1[28],
#                 writedisk_time=h1[29],
#                 nic1_datasent_size=h1[30],
#                 nic1_datasent_num=h1[31],
#                 nic1_datareceived_size=h1[32],
#                 nic1_datareceived_num=h1[33],
#                 nic1_datareceived_error=h1[34],
#                 nic1_datasent_error=h1[35],
#                 nic2_datasent_size=h1[36],
#                 nic2_datasent_num=h1[37],
#                 nic2_datareceived_size=h1[38],
#                 nic2_datareceived_num=h1[39],
#                 nic2_datareceived_error=h1[40],
#                 nic2_datasent_error=h1[41],
#                 nic3_datasent_size=h1[42],
#                 nic3_datasent_num=h1[43],
#                 nic3_datareceived_size=h1[44],
#                 nic3_datareceived_num=h1[45],
#                 nic3_datareceived_error=h1[46],
#                 nic3_datasent_error=h1[47],
#                 nic4_datasent_size=h1[48],
#                 nic4_datasent_num=h1[49],
#                 nic4_datareceived_size=h1[50],
#                 nic4_datareceived_num=h1[51],
#                 nic4_datareceived_error=h1[52],
#                 nic4_datasent_error=h1[53],
#                 nic5_datasent_size=h1[54],
#                 nic5_datasent_num=h1[55],
#                 nic5_datareceived_size=h1[56],
#                 nic5_datareceived_num=h1[57],
#                 nic5_datareceived_error=h1[58],
#                 nic5_datasent_error=h1[59],
#                 nic6_datasent_size=h1[60],
#                 nic6_datasent_num=h1[61],
#                 nic6_datareceived_size=h1[62],
#                 nic6_datareceived_num=h1[63],
#                 nic6_datareceived_error=h1[64],
#                 nic6_datasent_error=h1[65],
#                 nic7_datasent_size=h1[66],
#                 nic7_datasent_num=h1[67],
#                 nic7_datareceived_size=h1[68],
#                 nic7_datareceived_num=h1[69],
#                 nic7_datareceived_error=h1[70],
#                 nic7_datasent_error=h1[71],
#                 nic8_datasent_size=h1[72],
#                 nic8_datasent_num=h1[73],
#                 nic8_datareceived_size=h1[74],
#                 nic8_datareceived_num=h1[75],
#                 nic8_datareceived_error=h1[76],
#                 nic8_datasent_error=h1[77],
#                 nic9_datasent_size=h1[78],
#                 nic9_datasent_num=h1[79],
#                 nic9_datareceived_size=h1[80],
#                 nic9_datareceived_num=h1[81],
#                 nic9_datareceived_error=h1[82],
#                 nic9_datasent_error=h1[83]
#
#
#             )
#             for x in df1.itertuples():
#                 mysysteminfo.objects.create(
#                     timestamp=x[1],
#                     CPUlogics_num=x[2],
#                     CPUphysicals_num=x[3],
#                     CPU_usage=x[4],
#                     CPU_freq=x[5],
#                     UserMode_runtime=x[6],
#                     CoreState_runtime=x[7],
#                     IOwait_time=x[8],
#                     Averload_in1min=x[9],
#                     Averload_in5min=x[10],
#                     Averload_in15min=x[11],
#                     interruptions_num=x[12],
#                     softinterruptions_num=x[13],
#                     systemcalls_num=x[14],
#
#                     Totalmemory_size=x[15],
#                     Usedmemory_size=x[16],
#                     Freememory_size=x[17],
#                     Memory_usage=x[18],
#                     Swapmemory_size=x[19],
#                     UsedSwapmemory_size=x[20],
#                     FreeSwapmemory_size=x[21],
#                     Swapmemory_usage=x[22],
#
#                     Totaldisk_size=x[23],
#                     Useddisk_size=x[24],
#                     Freedisk_size=x[25],
#                     Disk_usage=x[26],
#                     readIO_size=x[27],
#                     writeIO_size=x[28],
#                     readdisk_time=x[29],
#                     writedisk_time=x[30],
#                     nic1_datasent_size=x[31],
#                     nic1_datasent_num=x[32],
#                     nic1_datareceived_size=x[33],
#                     nic1_datareceived_num=x[34],
#                     nic1_datareceived_error=x[35],
#                     nic1_datasent_error=x[36],
#                     nic2_datasent_size=x[37],
#                     nic2_datasent_num=x[38],
#                     nic2_datareceived_size=x[39],
#                     nic2_datareceived_num=x[40],
#                     nic2_datareceived_error=x[41],
#                     nic2_datasent_error=x[42],
#                     nic3_datasent_size=x[43],
#                     nic3_datasent_num=x[44],
#                     nic3_datareceived_size=x[45],
#                     nic3_datareceived_num=x[46],
#                     nic3_datareceived_error=x[47],
#                     nic3_datasent_error=x[48],
#                     nic4_datasent_size=x[49],
#                     nic4_datasent_num=x[50],
#                     nic4_datareceived_size=x[51],
#                     nic4_datareceived_num=x[52],
#                     nic4_datareceived_error=x[53],
#                     nic4_datasent_error=x[54],
#                     nic5_datasent_size=x[55],
#                     nic5_datasent_num=x[56],
#                     nic5_datareceived_size=x[57],
#                     nic5_datareceived_num=x[58],
#                     nic5_datareceived_error=x[59],
#                     nic5_datasent_error=x[60],
#                     nic6_datasent_size=x[61],
#                     nic6_datasent_num=x[62],
#                     nic6_datareceived_size=x[63],
#                     nic6_datareceived_num=x[64],
#                     nic6_datareceived_error=x[65],
#                     nic6_datasent_error=x[66],
#                     nic7_datasent_size=x[67],
#                     nic7_datasent_num=x[68],
#                     nic7_datareceived_size=x[69],
#                     nic7_datareceived_num=x[70],
#                     nic7_datareceived_error=x[71],
#                     nic7_datasent_error=x[72],
#                     nic8_datasent_size=x[73],
#                     nic8_datasent_num=x[74],
#                     nic8_datareceived_size=x[75],
#                     nic8_datareceived_num=x[76],
#                     nic8_datareceived_error=x[77],
#                     nic8_datasent_error=x[78],
#                     nic9_datasent_size=x[79],
#                     nic9_datasent_num=x[80],
#                     nic9_datareceived_size=x[81],
#                     nic9_datareceived_num=x[82],
#                     nic9_datareceived_error=x[83],
#                     nic9_datasent_error=x[84]
#
#
#                 )
#         elif internum == 10:
#             h1 = df1.columns.tolist()
#             mysysteminfo.objects.create(
#                 timestamp=h1[0],
#                 CPUlogics_num=h1[1],
#                 CPUphysicals_num=h1[2],
#                 CPU_usage=h1[3],
#                 CPU_freq=h1[4],
#                 UserMode_runtime=h1[5],
#                 CoreState_runtime=h1[6],
#                 IOwait_time=h1[7],
#                 Averload_in1min=h1[8],
#                 Averload_in5min=h1[9],
#                 Averload_in15min=h1[10],
#                 interruptions_num=h1[11],
#                 softinterruptions_num=h1[12],
#                 systemcalls_num=h1[13],
#
#                 Totalmemory_size=h1[14],
#                 Usedmemory_size=h1[15],
#                 Freememory_size=h1[16],
#                 Memory_usage=h1[17],
#                 Swapmemory_size=h1[18],
#                 UsedSwapmemory_size=h1[19],
#                 FreeSwapmemory_size=h1[20],
#                 Swapmemory_usage=h1[21],
#
#                 Totaldisk_size=h1[22],
#                 Useddisk_size=h1[23],
#                 Freedisk_size=h1[24],
#                 Disk_usage=h1[25],
#                 readIO_size=h1[26],
#                 writeIO_size=h1[27],
#                 readdisk_time=h1[28],
#                 writedisk_time=h1[29],
#                 nic1_datasent_size=h1[30],
#                 nic1_datasent_num=h1[31],
#                 nic1_datareceived_size=h1[32],
#                 nic1_datareceived_num=h1[33],
#                 nic1_datareceived_error=h1[34],
#                 nic1_datasent_error=h1[35],
#                 nic2_datasent_size=h1[36],
#                 nic2_datasent_num=h1[37],
#                 nic2_datareceived_size=h1[38],
#                 nic2_datareceived_num=h1[39],
#                 nic2_datareceived_error=h1[40],
#                 nic2_datasent_error=h1[41],
#                 nic3_datasent_size=h1[42],
#                 nic3_datasent_num=h1[43],
#                 nic3_datareceived_size=h1[44],
#                 nic3_datareceived_num=h1[45],
#                 nic3_datareceived_error=h1[46],
#                 nic3_datasent_error=h1[47],
#                 nic4_datasent_size=h1[48],
#                 nic4_datasent_num=h1[49],
#                 nic4_datareceived_size=h1[50],
#                 nic4_datareceived_num=h1[51],
#                 nic4_datareceived_error=h1[52],
#                 nic4_datasent_error=h1[53],
#                 nic5_datasent_size=h1[54],
#                 nic5_datasent_num=h1[55],
#                 nic5_datareceived_size=h1[56],
#                 nic5_datareceived_num=h1[57],
#                 nic5_datareceived_error=h1[58],
#                 nic5_datasent_error=h1[59],
#                 nic6_datasent_size=h1[60],
#                 nic6_datasent_num=h1[61],
#                 nic6_datareceived_size=h1[62],
#                 nic6_datareceived_num=h1[63],
#                 nic6_datareceived_error=h1[64],
#                 nic6_datasent_error=h1[65],
#                 nic7_datasent_size=h1[66],
#                 nic7_datasent_num=h1[67],
#                 nic7_datareceived_size=h1[68],
#                 nic7_datareceived_num=h1[69],
#                 nic7_datareceived_error=h1[70],
#                 nic7_datasent_error=h1[71],
#                 nic8_datasent_size=h1[72],
#                 nic8_datasent_num=h1[73],
#                 nic8_datareceived_size=h1[74],
#                 nic8_datareceived_num=h1[75],
#                 nic8_datareceived_error=h1[76],
#                 nic8_datasent_error=h1[77],
#                 nic9_datasent_size=h1[78],
#                 nic9_datasent_num=h1[79],
#                 nic9_datareceived_size=h1[80],
#                 nic9_datareceived_num=h1[81],
#                 nic9_datareceived_error=h1[82],
#                 nic9_datasent_error=h1[83],
#                 nic10_datasent_size=h1[84],
#                 nic10_datasent_num=h1[85],
#                 nic10_datareceived_size=h1[86],
#                 nic10_datareceived_num=h1[87],
#                 nic10_datareceived_error=h1[88],
#                 nic10_datasent_error=h1[89]
#
#             )
#             for x in df1.itertuples():
#                 mysysteminfo.objects.create(
#                     timestamp=x[1],
#                     CPUlogics_num=x[2],
#                     CPUphysicals_num=x[3],
#                     CPU_usage=x[4],
#                     CPU_freq=x[5],
#                     UserMode_runtime=x[6],
#                     CoreState_runtime=x[7],
#                     IOwait_time=x[8],
#                     Averload_in1min=x[9],
#                     Averload_in5min=x[10],
#                     Averload_in15min=x[11],
#                     interruptions_num=x[12],
#                     softinterruptions_num=x[13],
#                     systemcalls_num=x[14],
#
#                     Totalmemory_size=x[15],
#                     Usedmemory_size=x[16],
#                     Freememory_size=x[17],
#                     Memory_usage=x[18],
#                     Swapmemory_size=x[19],
#                     UsedSwapmemory_size=x[20],
#                     FreeSwapmemory_size=x[21],
#                     Swapmemory_usage=x[22],
#
#                     Totaldisk_size=x[23],
#                     Useddisk_size=x[24],
#                     Freedisk_size=x[25],
#                     Disk_usage=x[26],
#                     readIO_size=x[27],
#                     writeIO_size=x[28],
#                     readdisk_time=x[29],
#                     writedisk_time=x[30],
#                     nic1_datasent_size=x[31],
#                     nic1_datasent_num=x[32],
#                     nic1_datareceived_size=x[33],
#                     nic1_datareceived_num=x[34],
#                     nic1_datareceived_error=x[35],
#                     nic1_datasent_error=x[36],
#                     nic2_datasent_size=x[37],
#                     nic2_datasent_num=x[38],
#                     nic2_datareceived_size=x[39],
#                     nic2_datareceived_num=x[40],
#                     nic2_datareceived_error=x[41],
#                     nic2_datasent_error=x[42],
#                     nic3_datasent_size=x[43],
#                     nic3_datasent_num=x[44],
#                     nic3_datareceived_size=x[45],
#                     nic3_datareceived_num=x[46],
#                     nic3_datareceived_error=x[47],
#                     nic3_datasent_error=x[48],
#                     nic4_datasent_size=x[49],
#                     nic4_datasent_num=x[50],
#                     nic4_datareceived_size=x[51],
#                     nic4_datareceived_num=x[52],
#                     nic4_datareceived_error=x[53],
#                     nic4_datasent_error=x[54],
#                     nic5_datasent_size=x[55],
#                     nic5_datasent_num=x[56],
#                     nic5_datareceived_size=x[57],
#                     nic5_datareceived_num=x[58],
#                     nic5_datareceived_error=x[59],
#                     nic5_datasent_error=x[60],
#                     nic6_datasent_size=x[61],
#                     nic6_datasent_num=x[62],
#                     nic6_datareceived_size=x[63],
#                     nic6_datareceived_num=x[64],
#                     nic6_datareceived_error=x[65],
#                     nic6_datasent_error=x[66],
#                     nic7_datasent_size=x[67],
#                     nic7_datasent_num=x[68],
#                     nic7_datareceived_size=x[69],
#                     nic7_datareceived_num=x[70],
#                     nic7_datareceived_error=x[71],
#                     nic7_datasent_error=x[72],
#                     nic8_datasent_size=x[73],
#                     nic8_datasent_num=x[74],
#                     nic8_datareceived_size=x[75],
#                     nic8_datareceived_num=x[76],
#                     nic8_datareceived_error=x[77],
#                     nic8_datasent_error=x[78],
#                     nic9_datasent_size=x[79],
#                     nic9_datasent_num=x[80],
#                     nic9_datareceived_size=x[81],
#                     nic9_datareceived_num=x[82],
#                     nic9_datareceived_error=x[83],
#                     nic9_datasent_error=x[84],
#                     nic10_datasent_size=x[85],
#                     nic10_datasent_num=x[86],
#                     nic10_datareceived_size=x[87],
#                     nic10_datareceived_num=x[88],
#                     nic10_datareceived_error=x[89],
#                     nic10_datasent_error=x[90]
#                 )
#         elif internum == 11:
#             h1 = df1.columns.tolist()
#             mysysteminfo.objects.create(
#                 timestamp=h1[0],
#                 CPUlogics_num=h1[1],
#                 CPUphysicals_num=h1[2],
#                 CPU_usage=h1[3],
#                 CPU_freq=h1[4],
#                 UserMode_runtime=h1[5],
#                 CoreState_runtime=h1[6],
#                 IOwait_time=h1[7],
#                 Averload_in1min=h1[8],
#                 Averload_in5min=h1[9],
#                 Averload_in15min=h1[10],
#                 interruptions_num=h1[11],
#                 softinterruptions_num=h1[12],
#                 systemcalls_num=h1[13],
#
#                 Totalmemory_size=h1[14],
#                 Usedmemory_size=h1[15],
#                 Freememory_size=h1[16],
#                 Memory_usage=h1[17],
#                 Swapmemory_size=h1[18],
#                 UsedSwapmemory_size=h1[19],
#                 FreeSwapmemory_size=h1[20],
#                 Swapmemory_usage=h1[21],
#
#                 Totaldisk_size=h1[22],
#                 Useddisk_size=h1[23],
#                 Freedisk_size=h1[24],
#                 Disk_usage=h1[25],
#                 readIO_size=h1[26],
#                 writeIO_size=h1[27],
#                 readdisk_time=h1[28],
#                 writedisk_time=h1[29],
#                 nic1_datasent_size=h1[30],
#                 nic1_datasent_num=h1[31],
#                 nic1_datareceived_size=h1[32],
#                 nic1_datareceived_num=h1[33],
#                 nic1_datareceived_error=h1[34],
#                 nic1_datasent_error=h1[35],
#                 nic2_datasent_size=h1[36],
#                 nic2_datasent_num=h1[37],
#                 nic2_datareceived_size=h1[38],
#                 nic2_datareceived_num=h1[39],
#                 nic2_datareceived_error=h1[40],
#                 nic2_datasent_error=h1[41],
#                 nic3_datasent_size=h1[42],
#                 nic3_datasent_num=h1[43],
#                 nic3_datareceived_size=h1[44],
#                 nic3_datareceived_num=h1[45],
#                 nic3_datareceived_error=h1[46],
#                 nic3_datasent_error=h1[47],
#                 nic4_datasent_size=h1[48],
#                 nic4_datasent_num=h1[49],
#                 nic4_datareceived_size=h1[50],
#                 nic4_datareceived_num=h1[51],
#                 nic4_datareceived_error=h1[52],
#                 nic4_datasent_error=h1[53],
#                 nic5_datasent_size=h1[54],
#                 nic5_datasent_num=h1[55],
#                 nic5_datareceived_size=h1[56],
#                 nic5_datareceived_num=h1[57],
#                 nic5_datareceived_error=h1[58],
#                 nic5_datasent_error=h1[59],
#                 nic6_datasent_size=h1[60],
#                 nic6_datasent_num=h1[61],
#                 nic6_datareceived_size=h1[62],
#                 nic6_datareceived_num=h1[63],
#                 nic6_datareceived_error=h1[64],
#                 nic6_datasent_error=h1[65],
#                 nic7_datasent_size=h1[66],
#                 nic7_datasent_num=h1[67],
#                 nic7_datareceived_size=h1[68],
#                 nic7_datareceived_num=h1[69],
#                 nic7_datareceived_error=h1[70],
#                 nic7_datasent_error=h1[71],
#                 nic8_datasent_size=h1[72],
#                 nic8_datasent_num=h1[73],
#                 nic8_datareceived_size=h1[74],
#                 nic8_datareceived_num=h1[75],
#                 nic8_datareceived_error=h1[76],
#                 nic8_datasent_error=h1[77],
#                 nic9_datasent_size=h1[78],
#                 nic9_datasent_num=h1[79],
#                 nic9_datareceived_size=h1[80],
#                 nic9_datareceived_num=h1[81],
#                 nic9_datareceived_error=h1[82],
#                 nic9_datasent_error=h1[83],
#                 nic10_datasent_size=h1[84],
#                 nic10_datasent_num=h1[85],
#                 nic10_datareceived_size=h1[86],
#                 nic10_datareceived_num=h1[87],
#                 nic10_datareceived_error=h1[88],
#                 nic10_datasent_error=h1[89],
#                 nic11_datasent_size=h1[90],
#                 nic11_datasent_num=h1[91],
#                 nic11_datareceived_size=h1[92],
#                 nic11_datareceived_num=h1[93],
#                 nic11_datareceived_error=h1[94],
#                 nic11_datasent_error=h1[95]
#             )
#             for x in df1.itertuples():
#                 mysysteminfo.objects.create(
#                     timestamp=x[1],
#                     CPUlogics_num=x[2],
#                     CPUphysicals_num=x[3],
#                     CPU_usage=x[4],
#                     CPU_freq=x[5],
#                     UserMode_runtime=x[6],
#                     CoreState_runtime=x[7],
#                     IOwait_time=x[8],
#                     Averload_in1min=x[9],
#                     Averload_in5min=x[10],
#                     Averload_in15min=x[11],
#                     interruptions_num=x[12],
#                     softinterruptions_num=x[13],
#                     systemcalls_num=x[14],
#
#                     Totalmemory_size=x[15],
#                     Usedmemory_size=x[16],
#                     Freememory_size=x[17],
#                     Memory_usage=x[18],
#                     Swapmemory_size=x[19],
#                     UsedSwapmemory_size=x[20],
#                     FreeSwapmemory_size=x[21],
#                     Swapmemory_usage=x[22],
#
#                     Totaldisk_size=x[23],
#                     Useddisk_size=x[24],
#                     Freedisk_size=x[25],
#                     Disk_usage=x[26],
#                     readIO_size=x[27],
#                     writeIO_size=x[28],
#                     readdisk_time=x[29],
#                     writedisk_time=x[30],
#                     nic1_datasent_size=x[31],
#                     nic1_datasent_num=x[32],
#                     nic1_datareceived_size=x[33],
#                     nic1_datareceived_num=x[34],
#                     nic1_datareceived_error=x[35],
#                     nic1_datasent_error=x[36],
#                     nic2_datasent_size=x[37],
#                     nic2_datasent_num=x[38],
#                     nic2_datareceived_size=x[39],
#                     nic2_datareceived_num=x[40],
#                     nic2_datareceived_error=x[41],
#                     nic2_datasent_error=x[42],
#                     nic3_datasent_size=x[43],
#                     nic3_datasent_num=x[44],
#                     nic3_datareceived_size=x[45],
#                     nic3_datareceived_num=x[46],
#                     nic3_datareceived_error=x[47],
#                     nic3_datasent_error=x[48],
#                     nic4_datasent_size=x[49],
#                     nic4_datasent_num=x[50],
#                     nic4_datareceived_size=x[51],
#                     nic4_datareceived_num=x[52],
#                     nic4_datareceived_error=x[53],
#                     nic4_datasent_error=x[54],
#                     nic5_datasent_size=x[55],
#                     nic5_datasent_num=x[56],
#                     nic5_datareceived_size=x[57],
#                     nic5_datareceived_num=x[58],
#                     nic5_datareceived_error=x[59],
#                     nic5_datasent_error=x[60],
#                     nic6_datasent_size=x[61],
#                     nic6_datasent_num=x[62],
#                     nic6_datareceived_size=x[63],
#                     nic6_datareceived_num=x[64],
#                     nic6_datareceived_error=x[65],
#                     nic6_datasent_error=x[66],
#                     nic7_datasent_size=x[67],
#                     nic7_datasent_num=x[68],
#                     nic7_datareceived_size=x[69],
#                     nic7_datareceived_num=x[70],
#                     nic7_datareceived_error=x[71],
#                     nic7_datasent_error=x[72],
#                     nic8_datasent_size=x[73],
#                     nic8_datasent_num=x[74],
#                     nic8_datareceived_size=x[75],
#                     nic8_datareceived_num=x[76],
#                     nic8_datareceived_error=x[77],
#                     nic8_datasent_error=x[78],
#                     nic9_datasent_size=x[79],
#                     nic9_datasent_num=x[80],
#                     nic9_datareceived_size=x[81],
#                     nic9_datareceived_num=x[82],
#                     nic9_datareceived_error=x[83],
#                     nic9_datasent_error=x[84],
#                     nic10_datasent_size=x[85],
#                     nic10_datasent_num=x[86],
#                     nic10_datareceived_size=x[87],
#                     nic10_datareceived_num=x[88],
#                     nic10_datareceived_error=x[89],
#                     nic10_datasent_error=x[90],
#                     nic11_datasent_size=x[91],
#                     nic11_datasent_num=x[92],
#                     nic11_datareceived_size=x[93],
#                     nic11_datareceived_num=x[94],
#                     nic11_datareceived_error=x[95],
#                     nic11_datasent_error=x[96]
#
#
#                 )
#         elif internum == 12:
#             h1 = df1.columns.tolist()
#             mysysteminfo.objects.create(
#                 timestamp=h1[0],
#                 CPUlogics_num=h1[1],
#                 CPUphysicals_num=h1[2],
#                 CPU_usage=h1[3],
#                 CPU_freq=h1[4],
#                 UserMode_runtime=h1[5],
#                 CoreState_runtime=h1[6],
#                 IOwait_time=h1[7],
#                 Averload_in1min=h1[8],
#                 Averload_in5min=h1[9],
#                 Averload_in15min=h1[10],
#                 interruptions_num=h1[11],
#                 softinterruptions_num=h1[12],
#                 systemcalls_num=h1[13],
#
#                 Totalmemory_size=h1[14],
#                 Usedmemory_size=h1[15],
#                 Freememory_size=h1[16],
#                 Memory_usage=h1[17],
#                 Swapmemory_size=h1[18],
#                 UsedSwapmemory_size=h1[19],
#                 FreeSwapmemory_size=h1[20],
#                 Swapmemory_usage=h1[21],
#
#                 Totaldisk_size=h1[22],
#                 Useddisk_size=h1[23],
#                 Freedisk_size=h1[24],
#                 Disk_usage=h1[25],
#                 readIO_size=h1[26],
#                 writeIO_size=h1[27],
#                 readdisk_time=h1[28],
#                 writedisk_time=h1[29],
#                 nic1_datasent_size=h1[30],
#                 nic1_datasent_num=h1[31],
#                 nic1_datareceived_size=h1[32],
#                 nic1_datareceived_num=h1[33],
#                 nic1_datareceived_error=h1[34],
#                 nic1_datasent_error=h1[35],
#                 nic2_datasent_size=h1[36],
#                 nic2_datasent_num=h1[37],
#                 nic2_datareceived_size=h1[38],
#                 nic2_datareceived_num=h1[39],
#                 nic2_datareceived_error=h1[40],
#                 nic2_datasent_error=h1[41],
#                 nic3_datasent_size=h1[42],
#                 nic3_datasent_num=h1[43],
#                 nic3_datareceived_size=h1[44],
#                 nic3_datareceived_num=h1[45],
#                 nic3_datareceived_error=h1[46],
#                 nic3_datasent_error=h1[47],
#                 nic4_datasent_size=h1[48],
#                 nic4_datasent_num=h1[49],
#                 nic4_datareceived_size=h1[50],
#                 nic4_datareceived_num=h1[51],
#                 nic4_datareceived_error=h1[52],
#                 nic4_datasent_error=h1[53],
#                 nic5_datasent_size=h1[54],
#                 nic5_datasent_num=h1[55],
#                 nic5_datareceived_size=h1[56],
#                 nic5_datareceived_num=h1[57],
#                 nic5_datareceived_error=h1[58],
#                 nic5_datasent_error=h1[59],
#                 nic6_datasent_size=h1[60],
#                 nic6_datasent_num=h1[61],
#                 nic6_datareceived_size=h1[62],
#                 nic6_datareceived_num=h1[63],
#                 nic6_datareceived_error=h1[64],
#                 nic6_datasent_error=h1[65],
#                 nic7_datasent_size=h1[66],
#                 nic7_datasent_num=h1[67],
#                 nic7_datareceived_size=h1[68],
#                 nic7_datareceived_num=h1[69],
#                 nic7_datareceived_error=h1[70],
#                 nic7_datasent_error=h1[71],
#                 nic8_datasent_size=h1[72],
#                 nic8_datasent_num=h1[73],
#                 nic8_datareceived_size=h1[74],
#                 nic8_datareceived_num=h1[75],
#                 nic8_datareceived_error=h1[76],
#                 nic8_datasent_error=h1[77],
#                 nic9_datasent_size=h1[78],
#                 nic9_datasent_num=h1[79],
#                 nic9_datareceived_size=h1[80],
#                 nic9_datareceived_num=h1[81],
#                 nic9_datareceived_error=h1[82],
#                 nic9_datasent_error=h1[83],
#                 nic10_datasent_size=h1[84],
#                 nic10_datasent_num=h1[85],
#                 nic10_datareceived_size=h1[86],
#                 nic10_datareceived_num=h1[87],
#                 nic10_datareceived_error=h1[88],
#                 nic10_datasent_error=h1[89],
#                 nic11_datasent_size=h1[90],
#                 nic11_datasent_num=h1[91],
#                 nic11_datareceived_size=h1[92],
#                 nic11_datareceived_num=h1[93],
#                 nic11_datareceived_error=h1[94],
#                 nic11_datasent_error=h1[95],
#                 nic12_datasent_size=h1[96],
#                 nic12_datasent_num=h1[97],
#                 nic12_datareceived_size=h1[98],
#                 nic12_datareceived_num=h1[99],
#                 nic12_datareceived_error=h1[100],
#                 nic12_datasent_error=h1[101]
#             )
#             for x in df1.itertuples():
#                 mysysteminfo.objects.create(
#                     timestamp=x[1],
#                     CPUlogics_num=x[2],
#                     CPUphysicals_num=x[3],
#                     CPU_usage=x[4],
#                     CPU_freq=x[5],
#                     UserMode_runtime=x[6],
#                     CoreState_runtime=x[7],
#                     IOwait_time=x[8],
#                     Averload_in1min=x[9],
#                     Averload_in5min=x[10],
#                     Averload_in15min=x[11],
#                     interruptions_num=x[12],
#                     softinterruptions_num=x[13],
#                     systemcalls_num=x[14],
#
#                     Totalmemory_size=x[15],
#                     Usedmemory_size=x[16],
#                     Freememory_size=x[17],
#                     Memory_usage=x[18],
#                     Swapmemory_size=x[19],
#                     UsedSwapmemory_size=x[20],
#                     FreeSwapmemory_size=x[21],
#                     Swapmemory_usage=x[22],
#
#                     Totaldisk_size=x[23],
#                     Useddisk_size=x[24],
#                     Freedisk_size=x[25],
#                     Disk_usage=x[26],
#                     readIO_size=x[27],
#                     writeIO_size=x[28],
#                     readdisk_time=x[29],
#                     writedisk_time=x[30],
#                     nic1_datasent_size=x[31],
#                     nic1_datasent_num=x[32],
#                     nic1_datareceived_size=x[33],
#                     nic1_datareceived_num=x[34],
#                     nic1_datareceived_error=x[35],
#                     nic1_datasent_error=x[36],
#                     nic2_datasent_size=x[37],
#                     nic2_datasent_num=x[38],
#                     nic2_datareceived_size=x[39],
#                     nic2_datareceived_num=x[40],
#                     nic2_datareceived_error=x[41],
#                     nic2_datasent_error=x[42],
#                     nic3_datasent_size=x[43],
#                     nic3_datasent_num=x[44],
#                     nic3_datareceived_size=x[45],
#                     nic3_datareceived_num=x[46],
#                     nic3_datareceived_error=x[47],
#                     nic3_datasent_error=x[48],
#                     nic4_datasent_size=x[49],
#                     nic4_datasent_num=x[50],
#                     nic4_datareceived_size=x[51],
#                     nic4_datareceived_num=x[52],
#                     nic4_datareceived_error=x[53],
#                     nic4_datasent_error=x[54],
#                     nic5_datasent_size=x[55],
#                     nic5_datasent_num=x[56],
#                     nic5_datareceived_size=x[57],
#                     nic5_datareceived_num=x[58],
#                     nic5_datareceived_error=x[59],
#                     nic5_datasent_error=x[60],
#                     nic6_datasent_size=x[61],
#                     nic6_datasent_num=x[62],
#                     nic6_datareceived_size=x[63],
#                     nic6_datareceived_num=x[64],
#                     nic6_datareceived_error=x[65],
#                     nic6_datasent_error=x[66],
#                     nic7_datasent_size=x[67],
#                     nic7_datasent_num=x[68],
#                     nic7_datareceived_size=x[69],
#                     nic7_datareceived_num=x[70],
#                     nic7_datareceived_error=x[71],
#                     nic7_datasent_error=x[72],
#                     nic8_datasent_size=x[73],
#                     nic8_datasent_num=x[74],
#                     nic8_datareceived_size=x[75],
#                     nic8_datareceived_num=x[76],
#                     nic8_datareceived_error=x[77],
#                     nic8_datasent_error=x[78],
#                     nic9_datasent_size=x[79],
#                     nic9_datasent_num=x[80],
#                     nic9_datareceived_size=x[81],
#                     nic9_datareceived_num=x[82],
#                     nic9_datareceived_error=x[83],
#                     nic9_datasent_error=x[84],
#                     nic10_datasent_size=x[85],
#                     nic10_datasent_num=x[86],
#                     nic10_datareceived_size=x[87],
#                     nic10_datareceived_num=x[88],
#                     nic10_datareceived_error=x[89],
#                     nic10_datasent_error=x[90],
#                     nic11_datasent_size=x[91],
#                     nic11_datasent_num=x[92],
#                     nic11_datareceived_size=x[93],
#                     nic11_datareceived_num=x[94],
#                     nic11_datareceived_error=x[95],
#                     nic11_datasent_error=x[96],
#                     nic12_datasent_size=x[97],
#                     nic12_datasent_num=x[98],
#                     nic12_datareceived_size=x[99],
#                     nic12_datareceived_num=x[100],
#                     nic12_datareceived_error=x[101],
#                     nic12_datasent_error=x[102]
#                 )
#
#
# # options('create')
#
