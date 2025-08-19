# wsaplus

Generate **WSA+** solar wind speed maps at **0.1 AU** from synoptic magnetograms.

- **Input**: FITS magnetogram (GONG or HMI)
- **Output**: 2D speed map (km/s) on a 360x180 grid (phi x theta)

---

## Install

**From PyPI** (recommended):
```bash
pip install wsaplus
```

---

## Model Checkpoint (Zenodo)

The **WSA+ model checkpoint** (wsaplus.pt) is hosted on Zenodo:
**DOI**: https://doi.org/10.5281/zenodo.16883042

Download wsaplus.pt and pass it via --checkpoint, or set the WSAPLUS_CHECKPOINT environment variable.

---

## Usage

Python:

```python
from wsaplus import generate_wsaplus_map
res = generate_wsaplus_map("/path/to/GONG_2065.fits", mag_type="GONG", checkpoint_path="/path/to/wsaplus.pt")
print(res.speed_kms.shape)  # (360, 180)
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
