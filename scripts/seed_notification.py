from omnichannel_powerhouse.notification_manager import NOTIFICATION_MANAGER, post_video_ready_notification_to_chat
from omnichannel_powerhouse.agent_commander.memory import list_sessions

notif = NOTIFICATION_MANAGER.add_notification(
    title="Video Ready: Wall Street Ka Asli Khel Jo 99% Retail Traders Ko Barbaad Karta Hai",
    message="Aapki documentary video (10.1 min, 177 strictly unique clips, ZERO repeats) tayyar hokar Silicon Pulse par Unlisted queue me register ho chuki hai!",
    channel_key="channel_trading",
    channel_name="Silicon Pulse",
    video_id="youtube_1792766639",
    video_url="https://studio.youtube.com/videos",
    duration_min=10.1,
    thumbnail_url="/output/tier1_channel_trading_1792765604_master_thumb_A_monopoly_cyan.jpg",
    notif_type="video_uploaded"
)
print('Notification added:', notif['id'])

sessions = list_sessions()
if sessions:
    target_sid = sessions[0]['id']
    post_video_ready_notification_to_chat(
        session_id=target_sid,
        channel_name='Silicon Pulse',
        title='Wall Street Ka Asli Khel Jo 99% Retail Traders Ko Barbaad Karta Hai',
        duration_min=10.1,
        video_url='https://studio.youtube.com/videos',
        video_path='output/tier1_channel_trading_1792765604_master.mp4'
    )
    print('Posted live message to session:', target_sid)
