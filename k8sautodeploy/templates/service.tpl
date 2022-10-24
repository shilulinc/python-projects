{% block service %}
apiVersion: v1
kind: Service
metadata:
  labels:
    app: {{ name }}
  name: {{ name }}
  namespace: {{ namespace }}
spec:
  ports:
  - name: tcp
    port: 80
    protocol: TCP
    targetPort: {{ containerPort }}
  {% if grpc is true %}
  - name: grpc
    port: 1024
    protocol: TCP
    targetPort: 1024
  {% endif %}
  selector:
    app: {{ name }}
  sessionAffinity: None
  type: ClusterIP
{% endblock %}



