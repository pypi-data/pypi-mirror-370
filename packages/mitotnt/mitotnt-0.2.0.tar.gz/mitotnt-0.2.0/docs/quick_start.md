# Quick Start

MitoTNT is a Python toolkit for analyzing the temporal dynamics of mitochondrial networks.  
It integrates with **MitoGraph** for per-frame segmentation, then performs **tracking, remodeling event detection, motility analysis, and ChimeraX visualization**.

This page walks through a typical workflow step by step.

---

## 1. Prepare your data

MitoTNT expects your raw time-lapse movie as a sequence of 3D image stacks (TIFF).  
Each frame in time should be placed in its own folder, with a single `.tif` inside:

```
frame_000/frame_000.tif
frame_001/frame_001.tif
frame_002/frame_002.tif
...

```

This format makes it easy for MitoGraph to write outputs back into each frame’s folder.  
Make sure you have MitoGraph installed and accessible in your PATH.

---

## 2. Segment mitochondria with MitoGraph

MitoGraph takes each 3D stack and generates:
- Surface meshes `.vtk` for visualization.
- Supporting `.gnet`, `.coo`, and `.txt` files describing network structure.

Run it through MitoTNT:

```python
import mitotnt

seg = mitotnt.MitoSegmenter('D:/GitHub/MitoTNT/test_data/mitograph', 
                            xy_pxl_size=0.145, z_pxl_size=0.145) # add image pixel sizes in microns/pixel

seg.run_mitograph_cpu(max_workers=10) # specify the number of threads
```

* `xy_pxl_size` and `z_pxl_size` are **microns per pixel**, important for scaling.
* By default, results are saved inside each frame folder.

You can preview segmentation results in **ChimeraX**:

```python
seg.visualize_segmented_data()
```
This generates a `.cxc` script for visual quality check of raw TIFFs alongside segmented surfaces.


## 3. Extract skeleton graphs

To prepare for tracking, you need to build graphs from MitoGraph outputs:

```python
skel = mitotnt.SkeletonizedMito(seg)
skel.extract_graphs()
```
These graphs capture mitochondria location and connectivity and are the inputs to tracking.

---

## 4. Track mitochondrial networks

Tracking links network fragments across timepoints using both spatial and network information:

```python
tracker = mitotnt.NetworkTracker(skel, frame_interval=3.3)  # frame interval in seconds per frame
tracked = tracker.run()
```

* The algorithm maps nodes across frames, building trajectories for each mitochondrial fragment.
* Results are written to: `mitotnt/mito_node_tracks.csv` (all node trajectories).

If you’ve already run once, reload results without recomputing to continue with the next sections:

```python
tracked = tracker.reload_results()
```

You can also restrict tracking to a subset of frames, or skip frames (useful for slower processes or faster processing).

```python
tracker = mitotnt.NetworkTracker(skel, frame_interval=3.3,
                                 start_frame=10, end_frame=30,
                                 tracking_interval=2)
```
---

## 5. Visualize in ChimeraX

MitoTNT can produce ready-to-load visualization scripts for **UCSF ChimeraX**:

```python
viz = mitotnt.Visualizer(tracked)
viz.generate_chimerax_skeleton()  # skeleton structure
viz.generate_tracking_arrows()  # tracking arrows
viz.visualize_tracking()  # build full .cxc script
```

This creates a script:

```
mitotnt/visualization/visualize_tracking.cxc
```

Open it in ChimeraX to interactively explore:

* **Raw fluorescence cloud** rendered for context.
* **Network skeletons** across time.
* **Tracking arrows** showing mitochondrial network movement.
---

## 6. Analyze remodeling and motility

Once tracking is complete, MitoTNT can quantify key mitochondrial behaviors:

```python
# Detect network remodeling (fusion & fission events)
tracked.detect_fusion_fission()

# Compute motility at three levels:
# node (voxel), segment (linear branch), fragment (connected component)
tracked.compute_mitochondria_diffusivity() 
```

Each analysis writes a CSV file:

* `remodeling_events.csv` → list of detected fusions/fissions.
* `node_diffusivity.csv`, `segment_diffusivity.csv`, `fragment_diffusivity.csv` → quantitative mobility measures.

These files can be imported for downstream analyses and plotting.

---


## Summary

1. Organize your movie into per-frame 3D stacks.
2. Run MitoGraph via `MitoSegmenter` to obtain skeletons.
3. Extract graphs with `SkeletonizedMito`.
4. Track fragments across frames using `NetworkTracker`.
5. Visualize skeletons and dynamics in ChimeraX with `Visualizer`.
6. Analyze remodeling events and motility with `TrackedMito`.
