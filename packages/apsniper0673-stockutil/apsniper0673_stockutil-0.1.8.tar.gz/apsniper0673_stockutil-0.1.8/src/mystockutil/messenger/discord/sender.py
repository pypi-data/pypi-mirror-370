import requests

class DiscordSender:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send(self, message):
        requests.post(self.webhook_url, json={"content": message})

# 황금비 대표        
gr_sender = DiscordSender('https://discord.com/api/webhooks/1347084901844779018/sqgHY3P14seiIPXd15-AIxIftRdfzFV9Or2fYtBB1XevLevpPweNJm9H5cdIW0HcKwj1')

# 황금비 개별
gr_entry_zero = DiscordSender('https://discord.com/api/webhooks/1362630337888260116/NPTk3V8wOKZ8sjS-g0o-4OSZgy7CFib83furIDONAomphFZGS9sdYwy6CaxLSkd0J2_s')
gr_entry_one = DiscordSender('https://discord.com/api/webhooks/1362666742978973796/uW_RoUBRSgwryY8L0QQy_W7YH6VjTuvyy8-iUgKJkShlYWaj4xz_G9BEnxN5axUFtO9i')
gr_entry_two = DiscordSender('https://discord.com/api/webhooks/1362666785362411610/oBK59j4o4_IJ_3Tuwny5vJEgZHWOfpRTBuTwt-sCSDH2GHEigWEWkIE3hZPUpJ9TgZlb')
gr_entry_three = DiscordSender('https://discord.com/api/webhooks/1362666807101751416/h5e4NoKMcQTClpFhQL10sg5GR-L-QQVBZj0pKTRTwfUZNq1vwVu4i9rJLLgaW7HhEog0')
gr_entry_four = DiscordSender('https://discord.com/api/webhooks/1362666830669287465/0WbVPFOYHfZzx-eBzyJ-nfiKF5iIjtiVHClocAT2wzKCeFtkB9yrg3mAMc10Wc9PqlUw')
gr_entry_five = DiscordSender('https://discord.com/api/webhooks/1362666854987862066/aFSajyALHttWjLabAl6UBebD7doiyOSj3gIFcqFGCaFiq6imBVsGOE0NG15jtuBfRKVo')
gr_entry_hf = DiscordSender('https://discord.com/api/webhooks/1354984972661952673/vIiCfFlh8gNNMtdyenZr_s6d_ENU37Bgab5y6bR_49i-XJ04zCU2HUPiDb_F-Rx0E2RN')

gr_exit_zero = DiscordSender('https://discord.com/api/webhooks/1374232079012986960/BaT5zEcIUrCDYzFfHpgS1GPhZFNKdLfunpY8gbIaja4K3QsdU7sdySJWD2aGpfpwalZi')
gr_exit_one = DiscordSender('https://discord.com/api/webhooks/1374238305100627998/oC2dpWdkUDvgz5g0glB-SJmjgvrXINi73cNpHHYEo0VW3jhsGxMswBohsqy84LTlRFnZ')
gr_exit_two = DiscordSender('https://discord.com/api/webhooks/1374238355478548601/-RK0X7wHTC7OAKBAnXCb4Sa46F1UutdmJhrTiGBUDh1ypLpEj6RmuA1m9pDH8R4X0jOj')
gr_exit_three = DiscordSender('https://discord.com/api/webhooks/1374238411682222181/A0F2OWzdYonp-1-N6B1mfXlajhLelL8sTlvRFlAnHCohfgL_yViPyfe6k322H3UENnsf')
gr_exit_four = DiscordSender('https://discord.com/api/webhooks/1374238464278528020/IMO8inC-CEOLweQg-AfyeHK-4Cj1ynXqaWjVpVxoqRet4NNG872toy9m_ZvUjK1IOsOI')
gr_exit_five = DiscordSender('https://discord.com/api/webhooks/1374238519794340004/ptC2C2LSiTeUiktTo2-O1ByBegM9IOFs2AcIbdW1w-1MgUh6cZ6jlEyKxQy_xTHNT0ky')


# Scheduler sender
ms_sender = DiscordSender('https://discord.com/api/webhooks/1347085128509165579/Tqo-NevMGrQ5HZXjaAVfMk4t5-OW2C_zNzCVeT9z0-HwQwvJcov0u2qKxNkdTCKaghrf')
ss_sender = DiscordSender('https://discord.com/api/webhooks/1353572795178549288/GLrhkNAHMbmlMrpf2JLQ_7Zuns-fHthmUT_Vq7UnCsFU3keEDywxmci2yyPeXfLWVnhV')

# gr_two = DiscordSender('https://discord.com/api/webhooks/1354984967373066373/0NLNQJ_7UIoV-yt53TIIw9ZyGleHgkbTnFzJ8v_JdXdJUfLEQgqzCizSoV4F9MhA3pPi')
# gr_three = DiscordSender('https://discord.com/api/webhooks/1357226724496244837/9GrTKJjgUD8bGd8uxEWc-FBVV_iZ6-SGYj40b3b8H3EE7YsrLkk3jh7BOn7_wIR6B7R9')
# gr_four = DiscordSender('https://discord.com/api/webhooks/1359768724751650847/ykUDJIMzNoI1W98p4cVBoHz4kDFqXmsLFf_UmSS2d5muHDINyyipWTqTUswOyyP1Ev9C')
# gr_five = DiscordSender('https://discord.com/api/webhooks/1359768729948258354/seFMt3APXQY4HE6tjWmwhAig5HAlyxlAXd8Ayjy8gIFLD_SE6btxJD9yhBkdeu4U_JFT')
# gr_hf = DiscordSender('https://discord.com/api/webhooks/1354984972661952673/vIiCfFlh8gNNMtdyenZr_s6d_ENU37Bgab5y6bR_49i-XJ04zCU2HUPiDb_F-Rx0E2RN')

if __name__ == '__main__':
    senders = [gr_sender, ms_sender]
    for sender in senders:
        sender.send("Hello, World!")
        sender.send("This is a test message.")