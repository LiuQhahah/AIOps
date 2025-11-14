{{/*
Expand the name of the chart.
*/}}
{{- define "opsagent.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "opsagent.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "opsagent.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "opsagent.labels" -}}
helm.sh/chart: {{ include "opsagent.chart" . }}
{{ include "opsagent.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- with .Values.labels }}
{{ toYaml . }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "opsagent.selectorLabels" -}}
app.kubernetes.io/name: {{ include "opsagent.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: opsagent
component: ops-automation
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "opsagent.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "opsagent.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the secret to use
*/}}
{{- define "opsagent.secretName" -}}
{{- if .Values.existingSecret }}
{{- .Values.existingSecret }}
{{- else }}
{{- include "opsagent.fullname" . }}-secrets
{{- end }}
{{- end }}

{{/*
Create the name of the configmap to use
*/}}
{{- define "opsagent.configMapName" -}}
{{- include "opsagent.fullname" . }}-config
{{- end }}

{{/*
Return the proper image name
*/}}
{{- define "opsagent.image" -}}
{{- $registryName := .Values.image.registry | default "" -}}
{{- $repositoryName := .Values.image.repository -}}
{{- $tag := .Values.image.tag | default .Chart.AppVersion -}}
{{- if $registryName }}
{{- printf "%s/%s:%s" $registryName $repositoryName $tag -}}
{{- else }}
{{- printf "%s:%s" $repositoryName $tag -}}
{{- end }}
{{- end }}
