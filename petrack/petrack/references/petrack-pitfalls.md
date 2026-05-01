# PeTrack Pitfalls

Use this reference to diagnose common PeTrack problems.

## Planning Pitfalls

| Problem | Consequence | Prevention |
| --- | --- | --- |
| Automatic camera settings | Calibration and recognition drift during recording | Use manual focus, exposure, gain, white balance, and fixed resolution. |
| Marker colors in clothing or floor | False detections | Control clothing and scene colors before recording. |
| Low marker resolution | Code IDs unreadable | Test marker recognition at true camera distance. |
| Poor lighting or shadows | Recognition noise and tracking loss | Use uniform diffuse light and avoid daylight changes. |
| No synchronization event | Multi-camera or sensor fusion becomes uncertain | Record clock/audio/visual sync events repeatedly. |
| Missing calibration footage | World-coordinate accuracy cannot be recovered reliably | Record intrinsic and extrinsic material on site. |

## Calibration Pitfalls

| Problem | Symptom | Fix |
| --- | --- | --- |
| Intrinsic samples cover only image center | good center, poor borders | Use images covering entire area of interest. |
| Extrinsic point order mismatch | shifted or distorted world coordinates | Re-click image points in `.3dc` row order. |
| Inaccurate measured points | high extrinsic error | Recheck field measurements and outliers. |
| Camera moved after calibration | wrong trajectory coordinates | Recalibrate extrinsic after movement. |
| Origin/units undocumented | downstream interpretation errors | Record coordinate origin and use centimeters in `.3dc`. |

## Recognition Pitfalls

| Problem | Symptom | Fix |
| --- | --- | --- |
| Recognition ROI outside tracking ROI | one-point trajectories | Make tracking ROI larger than recognition ROI. |
| Morphology tuned while selecting color | unstable color mask | Disable open/close until color range is selected. |
| Wrong ArUco dictionary | missing code marker IDs | Select dictionary used to print markers. |
| Code marker too small or blurry | red candidates or no IDs | Improve focus/resolution, use multicolor fallback, or tune thresholding. |
| Height map missing | perspective errors, especially near borders | Assign color/ID heights or document default height. |

## Tracking Pitfalls

| Problem | Symptom | Fix |
| --- | --- | --- |
| Search region too small | track loss at normal movement | Increase scale or adjust levels. |
| Search region too broad | wrong head followed | Reduce scale or improve recognition frequency. |
| Flat marker texture | optical flow weak | Include edges/borders in search region. |
| `calculate all` run too early | large correction burden | Tune on representative segments first. |
| Active recognition/tracking during correction | manual edits overwritten | Disable active boxes before correction. |

## Correction Pitfalls

| Problem | Symptom | Fix |
| --- | --- | --- |
| Reviewing all people at once | missed errors | Use show-only controls one person at a time. |
| Deleting trajectories changes IDs | annotation/group mismatches | Finish trajectory correction before annotation groups. |
| Not saving `.trc` during correction | lost manual work | Export `.trc` regularly. |
| Treating tests as definitive | valid unusual behavior removed | Use correction tab output as candidates for visual review. |

## Export Pitfalls

| Problem | Symptom | Fix |
| --- | --- | --- |
| Using `.trc` as external analysis input | fragile parser or missing assumptions | Export `.txt` or HDF5. |
| Wrong units | density/speed values off by factor 100 | Use meter export for analysis unless centimeters are required. |
| Repeated smoothing | trajectories altered more than intended | Export from unsmoothed working data or document smoothing once. |
| Missing marker IDs | cannot link participants to metadata | Enable marker ID export when code markers are used. |
| Ignored dropped frames | time axis mismatch | Use missing-frame option if frame drops occurred and log the choice. |
