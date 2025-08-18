"use strict";
(self["webpackChunkbooking_extension"] = self["webpackChunkbooking_extension"] || []).push([["lib_index_js"],{

/***/ "./lib/components/DiskSpaceWidget.js":
/*!*******************************************!*\
  !*** ./lib/components/DiskSpaceWidget.js ***!
  \*******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ DiskSpaceWidget),
/* harmony export */   diskWidget: () => (/* binding */ diskWidget)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../handler */ "./lib/handler.js");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _utils_formatBytes__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../utils/formatBytes */ "./lib/utils/formatBytes.js");




const POLLING_INTERVAL = 60 * 10 ** 3; // Each minute
function DiskSpaceWidget() {
    const [diskInfo, setDiskInfo] = react__WEBPACK_IMPORTED_MODULE_0__.useState(null);
    react__WEBPACK_IMPORTED_MODULE_0__.useEffect(() => {
        const updateDiskInfo = () => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)('disk').then(val => setDiskInfo(val));
        updateDiskInfo();
        const interval = setInterval(updateDiskInfo, POLLING_INTERVAL);
        return () => clearInterval(interval);
    }, []);
    if (diskInfo == null)
        return react__WEBPACK_IMPORTED_MODULE_0__.createElement(react__WEBPACK_IMPORTED_MODULE_0__.Fragment, null);
    const spaceRatio = diskInfo.used / diskInfo.total;
    let className = 'booking-ds';
    if (spaceRatio >= 0.5)
        className = 'booking-ds warn';
    if (spaceRatio >= 0.75)
        className = 'booking-ds warn-2';
    if (spaceRatio >= 0.9)
        className = 'booking-ds warn-3';
    return (react__WEBPACK_IMPORTED_MODULE_0__.createElement("div", { className: className },
        react__WEBPACK_IMPORTED_MODULE_0__.createElement("span", null,
            (0,_utils_formatBytes__WEBPACK_IMPORTED_MODULE_3__.formatBytes)(diskInfo.used),
            "/",
            (0,_utils_formatBytes__WEBPACK_IMPORTED_MODULE_3__.formatBytes)(diskInfo.total),
            " (",
            (0,_utils_formatBytes__WEBPACK_IMPORTED_MODULE_3__.formatBytes)(diskInfo.free),
            " available)")));
}
const diskWidget = _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.ReactWidget.create(react__WEBPACK_IMPORTED_MODULE_0__.createElement(DiskSpaceWidget, null));
diskWidget.id = 'booking-widget';



/***/ }),

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   requestAPI: () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = '', init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'booking-extension', // API Namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    let data = await response.text();
    if (data.length > 0) {
        try {
            data = JSON.parse(data);
        }
        catch (error) {
            console.log('Not a JSON response body.', response);
        }
    }
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/statusbar */ "webpack/sharing/consume/default/@jupyterlab/statusbar");
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components_DiskSpaceWidget__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./components/DiskSpaceWidget */ "./lib/components/DiskSpaceWidget.js");
/* harmony import */ var _utils_showDiskNotifications__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./utils/showDiskNotifications */ "./lib/utils/showDiskNotifications.js");


// import { IThemeManager } from '@jupyterlab/apputils';


/**
 * Initialization data for the booking_extension extension.
 */
const plugin = {
    id: 'booking_extension:plugin',
    description: '',
    autoStart: true,
    optional: [_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_0__.ISettingRegistry, _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_1__.IStatusBar],
    activate: (app, settingRegistry, statusBar) => {
        console.log('JupyterLab extension booking_extension is activated!');
        if (settingRegistry) {
            settingRegistry
                .load(plugin.id)
                .then(settings => {
                console.log('booking_extension settings loaded:', settings.composite);
            })
                .catch(reason => {
                console.error('Failed to load settings for booking_extension.', reason);
            });
        }
        if (statusBar != null) {
            statusBar.registerStatusItem(_components_DiskSpaceWidget__WEBPACK_IMPORTED_MODULE_2__.diskWidget.id, {
                item: _components_DiskSpaceWidget__WEBPACK_IMPORTED_MODULE_2__.diskWidget,
                align: 'left',
                rank: 2
            });
        }
        (0,_utils_showDiskNotifications__WEBPACK_IMPORTED_MODULE_3__.showDiskNotifications)();
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/utils/formatBytes.js":
/*!**********************************!*\
  !*** ./lib/utils/formatBytes.js ***!
  \**********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   formatBytes: () => (/* binding */ formatBytes)
/* harmony export */ });
function formatBytes(bytes) {
    if (bytes < 0) {
        throw new Error('Bytes value must be non-negative');
    }
    const units = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const threshold = 1024;
    if (bytes < threshold) {
        return `${bytes} ${units[0]}`;
    }
    let unitIndex = 0;
    while (bytes >= threshold && unitIndex < units.length - 1) {
        bytes /= threshold;
        unitIndex++;
    }
    // Round to 2 decimal places and remove trailing .00 if needed
    const formattedValue = bytes % 1 === 0 ? bytes.toString() : bytes.toFixed(2).replace(/\.?0+$/, '');
    return `${formattedValue} ${units[unitIndex]}`;
}


/***/ }),

/***/ "./lib/utils/showDiskNotifications.js":
/*!********************************************!*\
  !*** ./lib/utils/showDiskNotifications.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   showDiskNotifications: () => (/* binding */ showDiskNotifications)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../handler */ "./lib/handler.js");


const POLLING_INTERVAL = 5 * 60 * 10 ** 3; // 5 minutes
function showDiskNotifications() {
    let notificationId = null;
    async function pollNotification() {
        if (notificationId != null) {
            const notifications = _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Notification.manager.notifications;
            const notificationsId = notifications.map(n => n.id);
            if (notificationsId.includes(notificationId))
                return;
        }
        const { used, total } = await (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)('disk');
        if (used / total < 0.95)
            return;
        notificationId = _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Notification.warning('Your storage is nearly full. You may have trouble saving files or installing apps. Free up space to avoid issues.', {
            autoClose: 5000
        });
        console.log(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Notification.manager.notifications);
    }
    pollNotification();
    setInterval(pollNotification, POLLING_INTERVAL);
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.e52dcac7bac22ffc2fa5.js.map