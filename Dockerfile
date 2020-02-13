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
    apt-get install -y pigz dcm2niix=1:1.0.20190902-1~nd18.04+1

RUN apt-get update && \
    apt-get install -y curl wget && \
    curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get remove -y curl && \
    apt-get install -y nodejs


RUN wget --quiet \
      https://repo.anaconda.com/miniconda/Miniconda3-4.7.12.1-Linux-x86_64.sh \
      -O anaconda.sh && \
    /bin/bash anaconda.sh -b -p /usr/local/anaconda && \
    rm anaconda.sh
ENV PATH=/usr/local/anaconda/bin:$PATH

RUN conda install pandas==0.25.1 numpy==1.16.4 xlrd
RUN pip install nibabel==2.4.1 pybids==0.9.4
RUN conda install --channel conda-forge nipype==1.2.3

RUN conda install git
RUN pip install https://github.com/poldracklab/pydeface/archive/v1.1.0.zip

RUN conda install pytest

RUN npm install -g bids-validator@1.3.8

COPY lhab_pipelines /code/lhab_pipelines/lhab_pipelines
COPY scripts /code/lhab_pipelines/scripts
COPY version /code/lhab_pipelines/version
ENV PYTHONPATH=/code/lhab_pipelines:$PYTHONPATH
CMD ["/bin/bash"]
