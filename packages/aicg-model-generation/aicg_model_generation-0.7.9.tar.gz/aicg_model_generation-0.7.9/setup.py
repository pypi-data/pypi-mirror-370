import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
# pypi-AgEIcHlwaS5vcmcCJGUzZDM4YWE4LThlN2QtNGZhNC1hYzVjLTY3ZDE4OTVhZDdiMgACKlszLCJmYmQ0M2NkMS0zZDFmLTQzMjMtYWEyMi1iYzZhNmFhN2IwYTIiXQAABiDNe5pwnhBWVbWlQPnVUaLccLizVzTEn041CBd7aMNVGg
setuptools.setup(
    name="aicg-model-generation",
    version="0.7.9",
    author="aicg",
    author_email="aicg@qq.com",
    description="new sdf package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    # packages=setuptools.find_packages(),
    packages=setuptools.find_packages(
        include=['AICGRender*'],  # 包括 AICGRender 及其所有子包
    ),
    
    package_data={
        'AICGRender.src.indoor_gaussian': ['base_config.yaml', 'indoor_re.yaml'],
        'AICGRender.src.object_gaussian.nerfstudio.configs': ['base.yaml', 'game1.yaml'],
        'AICGRender.pyarmor_runtime_009045': ['pyarmor_runtime.so']
    },

    install_requires=[
        "opencv-python",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

    #  pip install  git+https://github.com/eriksandstroem/evaluate_3d_reconstruction_lib.git@9b3cc08be5440db9c375cc21e3bd65bb4a337db7
    #  pip install  git+https://gitlab.inria.fr/bkerbl/simple-knn.git@f155ec04131cb579f53443a06879d37115f4612f
    #  pip install  git+https://github.com/VladimirYugay/gaussian_rasterizer.git@9c40173fcc8d9b16778a1a8040295bc2f9ebf129

    # sudo apt-get -y install cudnn-cuda-11
    # pip install git+https://github.com/hbb1/diff-surfel-rasterization.git@e0ed0207b3e0669960cfad70852200a4a5847f61
    # pip install git+https://github.com/rmurai0610/diff-gaussian-rasterization-w-pose.git@43e21bff91cd24986ee3dd52fe0bb06952e50ec
    # git+https://github.com/graphdeco-inria/diff-gaussian-rasterization@9c5c2028f6fbee2be239bc4c9421ff894fe4fbe0
     # git+https://github.com/rahul-goel/fused-ssim@1272e21a282342e89537159e4bad508b19b34157
      # git+https://github.com/hbb1/diff-surfel-rasterization@e0ed0207b3e0669960cfad70852200a4a5847f61
       # git+https://gitlab.inria.fr/bkerbl/simple-knn.git@f155ec04131cb579f53443a06879d37115f4612f
