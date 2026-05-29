FROM --platform=linux/amd64 freesurfer/freesurfer:8.2.0 AS freesurfer

FROM --platform=linux/amd64 python:3.11-slim

# Avoid .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FREESURFER_HOME=/usr/local/freesurfer/8.2.0-1/ \
    PATH=/usr/local/freesurfer/8.2.0-1/bin:$PATH

WORKDIR /workspace

# Install OS dependencies needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy SynthSeg-related FreeSurfer runtime files from build stage
COPY --from=freesurfer /usr/local/freesurfer/8.2.0-1/bin/mri_synthseg /usr/local/freesurfer/8.2.0-1/bin/mri_synthseg
COPY --from=freesurfer /usr/local/freesurfer/8.2.0-1/bin/fspython /usr/local/freesurfer/8.2.0-1/bin/fspython
COPY --from=freesurfer /usr/local/freesurfer/8.2.0-1/FreeSurferEnv.sh /usr/local/freesurfer/8.2.0-1/FreeSurferEnv.sh
COPY --from=freesurfer /usr/local/freesurfer/8.2.0-1/FreeSurferColorLUT.txt /usr/local/freesurfer/8.2.0-1/FreeSurferColorLUT.txt
COPY --from=freesurfer /usr/local/freesurfer/8.2.0-1/SetUpFreeSurfer.sh /usr/local/freesurfer/8.2.0-1/SetUpFreeSurfer.sh
COPY --from=freesurfer /usr/local/freesurfer/8.2.0-1/python /usr/local/freesurfer/8.2.0-1/python
COPY --from=freesurfer /usr/local/freesurfer/8.2.0-1/models/synthseg* /usr/local/freesurfer/8.2.0-1/models/

# Copy application source
COPY app/ ./app/

# Create runtime directories
RUN mkdir -p uploads outputs

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
