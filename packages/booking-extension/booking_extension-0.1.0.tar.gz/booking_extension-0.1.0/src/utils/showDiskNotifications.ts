import { Notification } from '@jupyterlab/apputils';
import { requestAPI } from '../handler';
import { DiskInfo } from '../components/DiskSpaceWidget';

const POLLING_INTERVAL = 5 * 60 * 10 ** 3; // 5 minutes

export function showDiskNotifications() {
  let notificationId: null | string = null;
  async function pollNotification() {
    if (notificationId != null) {
      const notifications = Notification.manager.notifications;
      const notificationsId = notifications.map(n => n.id);
      if (notificationsId.includes(notificationId)) return;
    }
    const { used, total } = await requestAPI<DiskInfo>('disk');
    if (used / total < 0.95) return;

    notificationId = Notification.warning(
      'Your storage is nearly full. You may have trouble saving files or installing apps. Free up space to avoid issues.',
      {
        autoClose: 5000
      }
    );
    console.log(Notification.manager.notifications);
  }

  pollNotification();

  setInterval(pollNotification, POLLING_INTERVAL);
}
