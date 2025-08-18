import * as React from 'react';
import { requestAPI } from '../handler';

import { ReactWidget } from '@jupyterlab/ui-components';
import { formatBytes } from '../utils/formatBytes';

export type DiskInfo = {
  free: number;
  total: number;
  used: number;
};

const POLLING_INTERVAL = 60 * 10 ** 3; // Each minute

export default function DiskSpaceWidget() {
  const [diskInfo, setDiskInfo] = React.useState<null | DiskInfo>(null);

  React.useEffect(() => {
    const updateDiskInfo = () =>
      requestAPI<DiskInfo>('disk').then(val => setDiskInfo(val));

    updateDiskInfo();
    const interval = setInterval(updateDiskInfo, POLLING_INTERVAL);
    return () => clearInterval(interval);
  }, []);

  if (diskInfo == null) return <></>;

  const spaceRatio = diskInfo.used / diskInfo.total;
  let className = 'booking-ds';
  if (spaceRatio >= 0.5) className = 'booking-ds warn';
  if (spaceRatio >= 0.75) className = 'booking-ds warn-2';
  if (spaceRatio >= 0.9) className = 'booking-ds warn-3';

  return (
    <div className={className}>
      <span>
        {formatBytes(diskInfo.used)}/{formatBytes(diskInfo.total)} (
        {formatBytes(diskInfo.free)} available)
      </span>
    </div>
  );
}

const diskWidget = ReactWidget.create(<DiskSpaceWidget />);
diskWidget.id = 'booking-widget';
export { diskWidget };
