{% block deployment %}
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: {{ name }}
    app_name: {{ name }}
  name: {{ name }}
  namespace: {{ namespace }}
spec:
  replicas: {{ replicaCount or 1 }}
  selector:
    matchLabels:
      app: {{ name }}
  strategy:
    rollingUpdate:
      maxSurge: {{ maxSurge }}
      maxUnavailable: {{ maxUnavailable }}
    type: RollingUpdate
  template:
    metadata:
      annotations:
      {% if metricsEnabled is true %}
        prometheus.io/port: {{ metricsPort  or 18089 }}
        prometheus.io/scrape: 'true'
      {% endif %}
      labels:
        app: {{ name }}
        app_name: {{ name }}
    spec:
      containers:
      - env:
{% if extraEnvVars %}
  {% for key in extraEnvVars %}{% if key['name'] == "APP_NAME" %}
        - name: APP_NAME
          value: {{ name }}
    {% elif key['name'] == "HTTP_PORT" %}
        - name: HTTP_PORT
          value: '8080'
    {% else %}
        - name: {{ key['name'] }}
          value: {{ key['value'] }}{% endif %}{% endfor %}
{% endif %}
        image: {{ imageRegistry or 'rcrai.tencentcloudcr.com' }}/{{ namespace or 'recurrent-customize' }}/{{ name }}:{{ imageTag or 'latest' }}:$VERSION
        imagePullPolicy: Always
        name: {{ name }}
        ports:
        - containerPort: 80
          protocol: TCP
{% if resources != '{}' and resources %}
        resources:
          {{ resources }}
{% endif %}
{% if livenessProbe['enabled'] is true %}
        livenessProbe:
          failureThreshold: {{ livenessProbe['failureThreshold'] }}
          httpGet:
            path: {{ livenessProbe['httpGet']['path'] }}
            port: {{ livenessProbe['httpGet']['port'] }}
            scheme: HTTP
          initialDelaySeconds: {{ livenessProbe['initialDelaySeconds'] }}
          periodSeconds: {{ livenessProbe['periodSeconds'] }}
          successThreshold: {{ livenessProbe['successThreshold'] }}
          timeoutSeconds: {{ livenessProbe['timeoutSeconds'] }}
{% endif %}
{% if readinessProbe['enabled'] is true %}
        readinessProbe:
          failureThreshold: {{ readinessProbe['failureThreshold'] }}
          httpGet:
            path: {{ readinessProbe['httpGet']['path'] }}
            port: {{ readinessProbe['httpGet']['port'] }}
            scheme: HTTP
          initialDelaySeconds: {{ readinessProbe['initialDelaySeconds'] }}
          periodSeconds: {{ readinessProbe['periodSeconds'] }}
          successThreshold: {{ readinessProbe['successThreshold'] }}
          timeoutSeconds: {{ readinessProbe['timeoutSeconds'] }}
{% endif %}
{% if staticSiteConfigmap['enabled'] is true %}
        volumeMounts:{% for config in staticSiteConfigmap['config'] %}
        - mountPath: {{ config['mountPath'] }}/{{ config['configName'] }}
          name: {{ config['appName'] or name }}-config
          {% if 'configName' in config %}subPath: {{ config['configName'] }}{% endif %}{% endfor %}{% endif %}
{% if staticSiteConfigmap['enabled'] is true %}
      volumes:{% for config in staticSiteConfigmap['config'] %}
      - configMap:
          defaultMode: 438
          name: {{ config['appName'] or name }}-config
        name: {{ config['appName'] or name }}-config{% endfor %}{% endif %}
      imagePullSecrets:
      - name: tke-docker-pull
      restartPolicy: Always
{% endblock %}
