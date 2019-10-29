FROM neurodebian:bionic-non-free

## FSL
RUN apt-get update && \
    apt-get install -y fsl-core=5.0.9-5~nd18.04+1

# Configure environment
ENV FSLDIR=/usr/share/fsl/5.0
ENV FSLOUTPUTTYPE=NIFTI_GZ
ENV PATH=/usr/lib/fsl/5.0:$PATH
ENV FSLMULTIFILEQUIT=TRUE
ENV POSSUMDIR=/usr/share/fsl/5.0
ENV LD_LIBRARY_PATH=/usr/lib/fsl/5.0:$LD_LIBRARY_PATH
ENV FSLTCLSH=/usr/bin/tclsh
ENV FSLWISH=/usr/bin/wish
ENV FSLOUTPUTTYPE=NIFTI_GZ

RUN apt-get update && \
    apt-get install -y dcm2niix=1:1.0.20190902-1~nd18.04+1

RUN apt-get update && \
    apt-get install -y curl wget && \
    curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get remove -y curl && \
    apt-get install -y nodejs


RUN wget --quiet \
      https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
      -O anaconda.sh && \
    /bin/bash anaconda.sh -b -p /usr/local/anaconda && \
    rm anaconda.sh
ENV PATH=/usr/local/anaconda/bin:$PATH

RUN conda install pandas numpy
RUN pip install nibabel pybids
RUN conda install --channel conda-forge nipype

RUN conda install git
RUN pip install git+https://github.com/poldracklab/pydeface.git@v1.1.0


COPY lhab_pipelines /code/lhab_pipelines/lhab_pipelines
COPY scripts /code/lhab_pipelines/scripts
COPY version /code/lhab_pipelines/version
ENV PYTHONPATH=/code/lhab_pipelines:$PYTHONPATH
CMD ["/bin/bash"]
