import argparse
import os
import numpy as np
from .api import generate_wsaplus_map


def main():
    parser = argparse.ArgumentParser(
        description="Generate WSA+ solar wind speed map at 0.1 AU from a synoptic magnetogram."
    )
    parser.add_argument("magnetogram", help="Path to synoptic magnetogram FITS file")
    parser.add_argument(
        "--mag-type", default="GONG", choices=["GONG", "HMI"], help="Magnetogram type"
    )
    parser.add_argument(
        "--checkpoint",
        help="Path to wsaplus model checkpoint (.pt). Download from Zenodo DOI https://doi.org/10.5281/zenodo.16883042 or set WSAPLUS_CHECKPOINT."
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Optional output file path. .npy will save numpy array; .fits saves FITS with simple header.",
    )
    parser.add_argument(
        "--n-cpu",
        type=int,
        default=None,
        help="Number of CPUs for PFSS tracing (overrides WSAPLUS_CPU; default=6)",
    )

    args = parser.parse_args()

    result = generate_wsaplus_map(
        magnetogram_path=args.magnetogram,
        mag_type=args.mag_type,
        checkpoint_path=args.checkpoint,
        n_cpu=args.n_cpu,
    )

    if args.output:
        out = args.output
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        if out.lower().endswith(".npy"):
            np.save(out, result.speed_kms)
            print(f"Saved WSA+ speed map to {out}")
        elif out.lower().endswith(".fits"):
            from astropy.io import fits

            hdu = fits.PrimaryHDU(result.speed_kms.astype(np.float32))
            hdr = hdu.header
            hdr["BUNIT"] = "km/s"
            hdr["COMMENT"] = "WSA+ speed at 0.1 AU; phi/theta grids in degrees not stored in header."
            hdu.writeto(out, overwrite=True)
            print(f"Saved WSA+ speed FITS to {out}")
        else:
            raise SystemExit("Unsupported output format. Use .npy or .fits")
    else:
        print("WSA+ speed map computed (not saved). Use --output to save.")


if __name__ == "__main__":
    main()
