# Planning And Recording Quality

Use this reference before advising on a new PeTrack experiment or auditing a
video that has already been recorded.

## Planning Checklist

| Topic | Check |
| --- | --- |
| Research need | Decide whether trajectories need only position, or also identity, height, head direction, or social grouping. |
| Location | Ensure enough camera height, stable mounting points, uniform lighting, and a floor/background that will not confuse marker detection. |
| Camera | Use fixed manual settings; avoid automatic focus, exposure, gain, or white balance during the experiment. |
| Markers | Choose marker type before recording; test marker visibility at real camera distance and resolution. |
| Calibration | Record intrinsic material after final camera settings; record extrinsic material after final camera position. |
| Synchronization | For multiple cameras or sensors, plan frame-level synchronization or repeated synchronization events. |
| Data handling | Plan storage, batteries/power, backups, and filenames before data collection. |

## Camera Geometry

PeTrack estimates head trajectories from images. The camera view should reduce
occlusion and perspective error:

- Prefer cameras mounted above the scene.
- Prefer smaller angle of view when coverage allows it.
- Increase mounting height or use overlapping cameras for large areas.
- Avoid severe border perspective when participant heights vary.
- For non-planar areas such as stairs, consider stereo or additional sensing.

## Camera Settings

Set camera parameters manually and keep them fixed:

| Setting | Practical guidance |
| --- | --- |
| Resolution | Must resolve the marker details; code markers need more pixels than colored hats. |
| Frame rate | Standard 24-30 fps is usually enough for walking; faster movement may need higher frame rate. |
| Focus | Focus at expected head height. |
| Aperture | Use settings that keep markers sharp across the field of view. |
| Shutter/exposure | Short enough to avoid motion blur; compatible with lighting to avoid flicker or brightness pumping. |
| Gain/ISO | Keep as low as lighting allows to reduce noise. |
| Recording format | Avoid interlaced recording; use a format that preserves marker sharpness. |

Changing camera settings after intrinsic calibration invalidates that
calibration.

## Lighting And Scene

- Use bright, uniform, diffuse lighting.
- Avoid daylight changes when possible.
- Avoid hard shadows, reflections, and high-contrast floor markings that can
  distract tracking.
- Keep marker colors out of clothing, floor colors, walls, and surrounding
  structures.
- Keep non-participants out of the tracked camera view, especially if they wear
  marker-like colors or hats.

## Marker Strategy

| Need | Marker choice |
| --- | --- |
| Robust detection with lower resolution | Multicolor marker |
| Individual identity, questionnaire linkage, head direction | Code marker |
| Robust fallback plus identity where resolution permits | Combined multicolor and code marker |
| No physical marker or custom pedestrian class | Machine-learning marker with ONNX model |

Test the chosen marker in PeTrack under the real camera distance, lighting, and
focus before the experiment. No full calibration is required for this detection
test.

## Calibration Recording

Intrinsic calibration:

- Record the calibration pattern with final camera settings.
- Cover the entire area of interest, including image borders.
- Use balanced samples; do not overrepresent one side of the image.
- Keep the pattern flat and sharp.

Extrinsic calibration:

- Record after cameras are mounted, aligned, and secured.
- Use measured world points that span the experimental area.
- Keep a sketch with point order and coordinates.
- Use a vertical pole or known-height reference when 3D points are needed.
- Record the time of calibration inside the experiment log.

## Multi-Camera Or Sensor Fusion

When combining PeTrack trajectories with questionnaires, sensors, or additional
camera views:

- Use individual marker IDs that stay consistent across experiments.
- Capture synchronization events in all relevant sensors.
- Use a common spatial coordinate system or document transforms.
- Record drift checks for long experiments.
- Keep marker ID to participant metadata in a separate controlled table.

## Data Preparation

- Keep raw video unchanged.
- Work on clipped copies if videos are very long; videos longer than about 15
  minutes can slow PeTrack work.
- Use stable naming for camera, run, calibration, and participant metadata.
- Back up raw video and calibration material before editing.
