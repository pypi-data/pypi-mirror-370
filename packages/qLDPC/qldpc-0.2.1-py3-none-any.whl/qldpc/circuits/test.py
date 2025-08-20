import os

import numpy as np
import sinter

from qldpc import circuits, codes

np.set_printoptions(linewidth=200)

if __name__ == "__main__":
    distance = 2
    prob = 10**-3.5

    code = codes.SurfaceCode(distance, rotated=True)
    strategy = circuits.EdgeColoring()
    noise_model = circuits.DepolarizingNoiseModel(prob, include_idling_error=False)

    circuit = circuits.memory_experiment(
        code, strategy, num_rounds=distance, noise_model=noise_model
    )
    dem = circuit.detector_error_model(decompose_errors=True)

    print(dem)
    print("num_detectors:", dem.num_detectors)
    print("num_errors:", dem.num_errors)

    sinter_decoder = circuits.sinter_decoder.SinterDecoder(with_BP_OSD=True)
    compiled_sinter_decoder = sinter_decoder.compile_decoder_for_dem(dem)

    distance = code.get_distance()
    task = sinter.Task(
        circuit=circuits.memory_experiment(code, strategy, distance, noise_model=noise_model),
        json_metadata={"d": code.get_distance(), "p": noise_model.p},
    )
    results = sinter.collect(
        # num_workers=os.cpu_count() - 1,
        num_workers=1,
        max_shots=10**6,
        max_errors=100,
        tasks=[task],
        decoders=["bplsd"],
        custom_decoders={
            "bplsd": circuits.SinterDecoder(
                with_BP_LSD=True,
                max_iter=30,
                bp_method="ms",
                lsd_method="lsd_cs",
                lsd_order=0,
            )
        },
    )
    print(results)
