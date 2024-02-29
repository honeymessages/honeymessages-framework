/* Feature FP uses ECMAScript 5 on purpose for compatibility reasons. */

var FEATURE_FP_VERSION = "2023-05-11_feature";
var FEATURE_FP_ENDPOINT = "browser_info/";

var feature_fp_data = [
	["feature_fp_version", FEATURE_FP_VERSION]
];

var feature_fp_globals = ["AbortController","AbortSignal","AbsoluteOrientationSensor","AbstractRange","Accelerometer","AnalyserNode","Animation","AnimationEffect","AnimationEvent","AnimationPlaybackEvent","AnimationTimeline","Attr","AudioBuffer","AudioBufferSourceNode","AudioContext","AudioData","AudioDecoder","AudioDestinationNode","AudioEncoder","AudioListener","AudioNode","AudioParam","AudioParamMap","AudioProcessingEvent","AudioScheduledSourceNode","AudioWorklet","AudioWorkletNode","AuthenticatorAssertionResponse","AuthenticatorAttestationResponse","AuthenticatorResponse","BackgroundFetchManager","BackgroundFetchRecord","BackgroundFetchRegistration","BarProp","BarcodeDetector","BaseAudioContext","BatteryManager","BeforeInstallPromptEvent","BeforeUnloadEvent","BiquadFilterNode","Blob","BlobEvent","Bluetooth","BluetoothCharacteristicProperties","BluetoothDevice","BluetoothRemoteGATTCharacteristic","BluetoothRemoteGATTDescriptor","BluetoothRemoteGATTServer","BluetoothRemoteGATTService","BluetoothUUID","BroadcastChannel","ByteLengthQueuingStrategy","CDATASection","CSS","CSSAnimation","CSSConditionRule","CSSCounterStyleRule","CSSFontFaceRule","CSSGroupingRule","CSSImageValue","CSSImportRule","CSSKeyframeRule","CSSKeyframesRule","CSSKeywordValue","CSSMathInvert","CSSMathMax","CSSMathMin","CSSMathNegate","CSSMathProduct","CSSMathSum","CSSMathValue","CSSMatrixComponent","CSSMediaRule","CSSNamespaceRule","CSSNumericArray","CSSNumericValue","CSSPageRule","CSSPerspective","CSSPositionValue","CSSPropertyRule","CSSRotate","CSSRule","CSSRuleList","CSSScale","CSSSkew","CSSSkewX","CSSSkewY","CSSStyleDeclaration","CSSStyleRule","CSSStyleSheet","CSSStyleValue","CSSSupportsRule","CSSTransformComponent","CSSTransformValue","CSSTransition","CSSTranslate","CSSUnitValue","CSSUnparsedValue","CSSVariableReferenceValue","Cache","CacheStorage","CanvasCaptureMediaStreamTrack","CanvasGradient","CanvasPattern","CanvasRenderingContext2D","ChannelMergerNode","ChannelSplitterNode","CharacterData","Clipboard","ClipboardEvent","ClipboardItem","CloseEvent","Comment","CompositionEvent","CompressionStream","console","ConstantSourceNode","ConvolverNode","CookieChangeEvent","CookieStore","CookieStoreManager","CountQueuingStrategy","Credential","CredentialsContainer","Crypto","CryptoKey","CustomElementRegistry","CustomEvent","CustomStateSet","DOMError","DOMException","DOMImplementation","DOMMatrix","DOMMatrixReadOnly","DOMParser","DOMPoint","DOMPointReadOnly","DOMQuad","DOMRect","DOMRectList","DOMRectReadOnly","DOMStringList","DOMStringMap","DOMTokenList","DataTransfer","DataTransferItem","DataTransferItemList","DecompressionStream","DelayNode","DeviceMotionEvent","DeviceOrientationEvent","Document","DocumentFragment","DocumentTimeline","DocumentType","DragEvent","DynamicsCompressorNode","Element","ElementInternals","EncodedAudioChunk","EncodedVideoChunk","ErrorEvent","Event","EventCounts","EventSource","EventTarget","External","EyeDropper","FeaturePolicy","FederatedCredential","File","FileList","FileReader","FileSystemDirectoryHandle","FileSystemFileHandle","FileSystemHandle","FileSystemWritableFileStream","FocusEvent","FontFace","FontFaceSetLoadEvent","FormData","FormDataEvent","FragmentDirective","GainNode","Gamepad","GamepadButton","GamepadEvent","GamepadHapticActuator","Geolocation","GeolocationCoordinates","GeolocationPosition","GeolocationPositionError","GravitySensor","Gyroscope","HID","HIDConnectionEvent","HIDDevice","HIDInputReportEvent","HTMLAllCollection","HTMLAnchorElement","HTMLAreaElement","HTMLAudioElement","HTMLBRElement","HTMLBaseElement","HTMLBodyElement","HTMLButtonElement","HTMLCanvasElement","HTMLCollection","HTMLDListElement","HTMLDataElement","HTMLDataListElement","HTMLDetailsElement","HTMLDialogElement","HTMLDirectoryElement","HTMLDivElement","HTMLDocument","HTMLElement","HTMLEmbedElement","HTMLFieldSetElement","HTMLFontElement","HTMLFormControlsCollection","HTMLFormElement","HTMLFrameElement","HTMLFrameSetElement","HTMLHRElement","HTMLHeadElement","HTMLHeadingElement","HTMLHtmlElement","HTMLIFrameElement","HTMLImageElement","HTMLInputElement","HTMLLIElement","HTMLLabelElement","HTMLLegendElement","HTMLLinkElement","HTMLMapElement","HTMLMarqueeElement","HTMLMediaElement","HTMLMenuElement","HTMLMetaElement","HTMLMeterElement","HTMLModElement","HTMLOListElement","HTMLObjectElement","HTMLOptGroupElement","HTMLOptionElement","HTMLOptionsCollection","HTMLOutputElement","HTMLParagraphElement","HTMLParamElement","HTMLPictureElement","HTMLPreElement","HTMLProgressElement","HTMLQuoteElement","HTMLScriptElement","HTMLSelectElement","HTMLSlotElement","HTMLSourceElement","HTMLSpanElement","HTMLStyleElement","HTMLTableCaptionElement","HTMLTableCellElement","HTMLTableColElement","HTMLTableElement","HTMLTableRowElement","HTMLTableSectionElement","HTMLTemplateElement","HTMLTextAreaElement","HTMLTimeElement","HTMLTitleElement","HTMLTrackElement","HTMLUListElement","HTMLUnknownElement","HTMLVideoElement","HashChangeEvent","Headers","History","IDBCursor","IDBCursorWithValue","IDBDatabase","IDBFactory","IDBIndex","IDBKeyRange","IDBObjectStore","IDBOpenDBRequest","IDBRequest","IDBTransaction","IDBVersionChangeEvent","IIRFilterNode","IdleDeadline","IdleDetector","ImageBitmap","ImageBitmapRenderingContext","ImageCapture","ImageData","ImageDecoder","ImageTrack","ImageTrackList","InputDeviceCapabilities","InputDeviceInfo","InputEvent","IntersectionObserver","IntersectionObserverEntry","Keyboard","KeyboardEvent","KeyboardLayoutMap","KeyframeEffect","LargestContentfulPaint","LayoutShift","LayoutShiftAttribution","LinearAccelerationSensor","Location","Lock","LockManager","MIDIAccess","MIDIConnectionEvent","MIDIInput","MIDIInputMap","MIDIMessageEvent","MIDIOutput","MIDIOutputMap","MIDIPort","MediaCapabilities","MediaDeviceInfo","MediaDevices","MediaElementAudioSourceNode","MediaEncryptedEvent","MediaError","MediaKeyMessageEvent","MediaKeySession","MediaKeyStatusMap","MediaKeySystemAccess","MediaKeys","MediaList","MediaMetadata","MediaQueryList","MediaQueryListEvent","MediaRecorder","MediaSession","MediaSource","MediaStream","MediaStreamAudioDestinationNode","MediaStreamAudioSourceNode","MediaStreamEvent","MediaStreamTrack","MediaStreamTrackEvent","MessageChannel","MessageEvent","MessagePort","MimeType","MimeTypeArray","MouseEvent","MutationEvent","MutationObserver","MutationRecord","NamedNodeMap","NavigationPreloadManager","Navigator","NavigatorUAData","NetworkInformation","Node","NodeFilter","NodeIterator","NodeList","Notification","OfflineAudioCompletionEvent","OfflineAudioContext","OffscreenCanvas","OffscreenCanvasRenderingContext2D","OrientationSensor","OscillatorNode","OverconstrainedError","PageTransitionEvent","PannerNode","PasswordCredential","Path2D","PaymentAddress","PaymentManager","PaymentMethodChangeEvent","PaymentRequest","PaymentRequestUpdateEvent","PaymentResponse","Performance","PerformanceElementTiming","PerformanceEntry","PerformanceEventTiming","PerformanceLongTaskTiming","PerformanceMark","PerformanceMeasure","PerformanceNavigation","PerformanceNavigationTiming","PerformanceObserver","PerformanceObserverEntryList","PerformancePaintTiming","PerformanceResourceTiming","PerformanceServerTiming","PerformanceTiming","PeriodicSyncManager","PeriodicWave","PermissionStatus","Permissions","PictureInPictureEvent","PictureInPictureWindow","Plugin","PluginArray","PointerEvent","PopStateEvent","Presentation","PresentationAvailability","PresentationConnection","PresentationConnectionAvailableEvent","PresentationConnectionCloseEvent","PresentationConnectionList","PresentationReceiver","PresentationRequest","ProcessingInstruction","ProgressEvent","PromiseRejectionEvent","PublicKeyCredential","PushManager","PushSubscription","PushSubscriptionOptions","RTCCertificate","RTCDTMFSender","RTCDTMFToneChangeEvent","RTCDataChannel","RTCDataChannelEvent","RTCDtlsTransport","RTCEncodedAudioFrame","RTCEncodedVideoFrame","RTCError","RTCErrorEvent","RTCIceCandidate","RTCIceTransport","RTCPeerConnection","RTCPeerConnectionIceErrorEvent","RTCPeerConnectionIceEvent","RTCRtpReceiver","RTCRtpSender","RTCRtpTransceiver","RTCSctpTransport","RTCSessionDescription","RTCStatsReport","RTCTrackEvent","RadioNodeList","Range","ReadableByteStreamController","ReadableStream","ReadableStreamBYOBReader","ReadableStreamBYOBRequest","ReadableStreamDefaultController","ReadableStreamDefaultReader","RelativeOrientationSensor","RemotePlayback","ReportingObserver","Request","ResizeObserver","ResizeObserverEntry","ResizeObserverSize","Response","SVGAElement","SVGAngle","SVGAnimateElement","SVGAnimateMotionElement","SVGAnimateTransformElement","SVGAnimatedAngle","SVGAnimatedBoolean","SVGAnimatedEnumeration","SVGAnimatedInteger","SVGAnimatedLength","SVGAnimatedLengthList","SVGAnimatedNumber","SVGAnimatedNumberList","SVGAnimatedPreserveAspectRatio","SVGAnimatedRect","SVGAnimatedString","SVGAnimatedTransformList","SVGAnimationElement","SVGCircleElement","SVGClipPathElement","SVGComponentTransferFunctionElement","SVGDefsElement","SVGDescElement","SVGElement","SVGEllipseElement","SVGFEBlendElement","SVGFEColorMatrixElement","SVGFEComponentTransferElement","SVGFECompositeElement","SVGFEConvolveMatrixElement","SVGFEDiffuseLightingElement","SVGFEDisplacementMapElement","SVGFEDistantLightElement","SVGFEDropShadowElement","SVGFEFloodElement","SVGFEFuncAElement","SVGFEFuncBElement","SVGFEFuncGElement","SVGFEFuncRElement","SVGFEGaussianBlurElement","SVGFEImageElement","SVGFEMergeElement","SVGFEMergeNodeElement","SVGFEMorphologyElement","SVGFEOffsetElement","SVGFEPointLightElement","SVGFESpecularLightingElement","SVGFESpotLightElement","SVGFETileElement","SVGFETurbulenceElement","SVGFilterElement","SVGForeignObjectElement","SVGGElement","SVGGeometryElement","SVGGradientElement","SVGGraphicsElement","SVGImageElement","SVGLength","SVGLengthList","SVGLineElement","SVGLinearGradientElement","SVGMPathElement","SVGMarkerElement","SVGMaskElement","SVGMatrix","SVGMetadataElement","SVGNumber","SVGNumberList","SVGPathElement","SVGPatternElement","SVGPoint","SVGPointList","SVGPolygonElement","SVGPolylineElement","SVGPreserveAspectRatio","SVGRadialGradientElement","SVGRect","SVGRectElement","SVGSVGElement","SVGScriptElement","SVGSetElement","SVGStopElement","SVGStringList","SVGStyleElement","SVGSwitchElement","SVGSymbolElement","SVGTSpanElement","SVGTextContentElement","SVGTextElement","SVGTextPathElement","SVGTextPositioningElement","SVGTitleElement","SVGTransform","SVGTransformList","SVGUnitTypes","SVGUseElement","SVGViewElement","Sanitizer","Scheduling","Screen","ScreenOrientation","ScriptProcessorNode","SecurityPolicyViolationEvent","Selection","Sensor","SensorErrorEvent","Serial","SerialPort","ServiceWorker","ServiceWorkerContainer","ServiceWorkerRegistration","ShadowRoot","SharedWorker","SourceBuffer","SourceBufferList","SpeechSynthesisErrorEvent","SpeechSynthesisEvent","SpeechSynthesisUtterance","StaticRange","StereoPannerNode","Storage","StorageEvent","StorageManager","StylePropertyMap","StylePropertyMapReadOnly","StyleSheet","StyleSheetList","SubmitEvent","SubtleCrypto","SyncManager","TaskAttributionTiming","Text","TextDecoder","TextDecoderStream","TextEncoder","TextEncoderStream","TextMetrics","TextTrack","TextTrackCue","TextTrackCueList","TextTrackList","TimeRanges","Touch","TouchEvent","TouchList","TrackEvent","TransformStream","TransformStreamDefaultController","TransitionEvent","TreeWalker","TrustedHTML","TrustedScript","TrustedScriptURL","TrustedTypePolicy","TrustedTypePolicyFactory","UIEvent","URL","URLPattern","URLSearchParams","USB","USBAlternateInterface","USBConfiguration","USBConnectionEvent","USBDevice","USBEndpoint","USBInTransferResult","USBInterface","USBIsochronousInTransferPacket","USBIsochronousInTransferResult","USBIsochronousOutTransferPacket","USBIsochronousOutTransferResult","USBOutTransferResult","VTTCue","ValidityState","VideoColorSpace","VideoDecoder","VideoEncoder","VideoFrame","VideoPlaybackQuality","VisualViewport","WakeLock","WakeLockSentinel","WaveShaperNode","WebGL2RenderingContext","WebGLActiveInfo","WebGLBuffer","WebGLContextEvent","WebGLFramebuffer","WebGLProgram","WebGLQuery","WebGLRenderbuffer","WebGLRenderingContext","WebGLSampler","WebGLShader","WebGLShaderPrecisionFormat","WebGLSync","WebGLTexture","WebGLTransformFeedback","WebGLUniformLocation","WebGLVertexArrayObject","WebKitCSSMatrix","WebSocket","WheelEvent","Window","Worker","Worklet","WritableStream","WritableStreamDefaultController","WritableStreamDefaultWriter","XMLDocument","XMLHttpRequest","XMLHttpRequestEventTarget","XMLHttpRequestUpload","XMLSerializer","XPathEvaluator","XPathExpression","XPathResult","XRAnchor","XRAnchorSet","XRBoundedReferenceSpace","XRCPUDepthInformation","XRDepthInformation","XRFrame","XRHitTestResult","XRHitTestSource","XRInputSource","XRInputSourceArray","XRInputSourceEvent","XRInputSourcesChangeEvent","XRLayer","XRLightEstimate","XRLightProbe","XRPose","XRRay","XRReferenceSpace","XRReferenceSpaceEvent","XRRenderState","XRRigidTransform","XRSession","XRSessionEvent","XRSpace","XRSystem","XRTransientInputHitTestResult","XRTransientInputHitTestSource","XRView","XRViewerPose","XRViewport","XRWebGLBinding","XRWebGLDepthInformation","XRWebGLLayer","XSLTProcessor","atob","btoa","caches","clearInterval","clearTimeout","createImageBitmap","crossOriginIsolated","crypto","fetch","indexedDB","isSecureContext","origin","performance","queueMicrotask","reportError","setInterval","setTimeout","trustedTypes","AggregateError","Array","ArrayBuffer","Atomics","BigInt","BigInt64Array","BigUint64Array","Boolean","DataView","Date","Error","EvalError","FinalizationRegistry","Float32Array","Float64Array","Function","Int16Array","Int32Array","Int8Array","JSON","Map","Number","Object","Promise","Proxy","RangeError","ReferenceError","Reflect","RegExp","Set","String","Symbol","SyntaxError","TypeError","URIError","Uint16Array","Uint32Array","Uint8Array","Uint8ClampedArray","WeakMap","WeakRef","WeakSet","Infinity","NaN","decodeURI","decodeURIComponent","encodeURI","encodeURIComponent","escape","eval","globalThis","isFinite","isNaN","parseFloat","parseInt","undefined","unescape","Intl","WebAssembly",];

function collectFeatures() {
	var features = "";
	for (var i in feature_fp_globals) {
		features += feature_fp_globals[i] in window ? "1" : "0";
	}
	feature_fp_data.push(["features", features]);
}

/**
 * Sends the fingerprint and additional data to an API endpoint.
 */
function reportFeatureFp() {
	function getCookie(a) {
		var b = document.cookie.match('(^|;)\\s*' + a + '\\s*=\\s*([^;]+)');
		return b ? b.pop() : '';
	}

	feature_fp_data.push(["visited_url", window.location.href]); // the url that issued the fingerprint

	// prepare xhr
	var xhr = new XMLHttpRequest();
	var url = window.location.pathname;
	url = url.endsWith("/") ? url : url + "/";
	xhr.open("POST", url + FEATURE_FP_ENDPOINT, true);

	// set csrf header
	xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));

	// send XHR to API endpoint
	xhr.send(JSON.stringify(feature_fp_data));
}

function collectBrowserInfo() {
	add("client_ua", "navigator.userAgent");
	add("platform", "navigator.platform");
	add("vendor", "navigator.vendor");
	add("languages", "navigator.languages");
	addAll("outer_res", ["outerWidth", "outerHeight"], "x");
	addAll("inner_res", ["innerWidth", "innerHeight"], "x");

	if (navigator.plugins === undefined) {
		feature_fp_data.push(["plugins", ""]);
	}
	else {
		var i, len = navigator.plugins.length, plugins = [];
		for(i=0;i<len;i++){
			plugins.push(navigator.plugins[i].name);
		}
		feature_fp_data.push(["plugins", plugins.join(",")]);
	}

	check("chrome", function() { return !!window.chrome });
	check("opera", function() { return !!window.opera });
	check("netscape", function() { return !!window.netscape });
	check("safari", function() { return !!window.safari });
	check("old_ie", function() { return !!window.attachEvent && !window.addEventListener });

	check("ie_like", function() { return /*@cc_on!@*/false || !!document.documentMode });
	check("safari_like", function() { return !!window.safari });
	check("mozilla_like", function() { return !!window.Components || typeof InstallTrigger !== 'undefined' });
	check("chrome_like", function() { return !((!(/*@cc_on!@*/false || !!document.documentMode) && !!window.StyleMedia) || top.msCredentials) && (!!window.chrome || /Chrome/.test(navigator.userAgent) || /Google/i.test(navigator.vendor))});
	check("opera_like", function() { return (!!window.opr && !!opr.addons) || (!!window.opera && window.opera.toString() === "[object Opera]")});
	check("edge_like", function() { return (!(/*@cc_on!@*/false || !!document.documentMode) && !!window.StyleMedia) || top.msCredentials });

	check("webdriver", function() { return !!navigator.webdriver || !!HTMLDocument.webdriver || !!window._WEBDRIVER_ELEM_CACHE });
	check("automation", function() { return !!window.domAutomationController || !!window.domAutomation });
	check("phantom", function() { return !!window.callPhantom || !!window._phantom || !!window._phantomas });
	check("nightmare", function() { return !!window.__nightmare });
	check("awesomium", function() { return !!window.awesomium });

	check("es5", function() { return Object.defineProperty });
	check("es6", function() { return eval("setTimeout(() => {null}, 1);") });
	check("es7", function() { return Array.prototype.includes !== undefined });
	check("es8", function() { return eval("(async function() {});") });
	check("es9", function() { return eval("let {rest_test, ...a_test} = Object; 1") });
	check("es10", function() { return "".matchAll });
}

function check(name, func) {
	var result = false;
	try {
		result = func();
	}
	catch(err) {}
	feature_fp_data.push([name, result ? "1" : "0"]);
}

function get(property) {
	var obj = window;
	var split = property.split(".");
	for (var i in split) {
		if (split[i] in obj) {
			obj = obj[split[i]];
		}
		else {
			throw new Error("Not found");
		}
	}
	return obj;
}

function add(name, property) {
	var value = "";
	try {
		value = get(property).toString();
	}
	catch(err) {}
	feature_fp_data.push([name, value]);
}

function addAll(name, properties, concat) {
	var value = "";
	for (var i in properties) {
		try {
			value += get(properties[i]).toString() + concat;
		}
		catch(err) {
			value = "";
			break;
		}
	}
	value = value.slice(0, -concat.length);
	feature_fp_data.push([name, value]);
}

(function run_feature_fp() {
	collectFeatures();
	collectBrowserInfo();
	reportFeatureFp();
})();
