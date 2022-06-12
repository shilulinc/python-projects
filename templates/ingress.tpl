{% block ingress %}
apiVersion: {{ apiVersion or "extensions/v1beta1" }}
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: {{ ingressClass or "prod-ingress-controller" }}
    {% if rewrite is true %}
    nginx.ingress.kubernetes.io/rewrite-target: {{ rewriteTargetPath }}
    {% endif %}
    nginx.ingress.kubernetes.io/proxy-body-size: 200m
    nginx.ingress.kubernetes.io/service-weight: ''

  name: {{ metadataName }}
  namespace: {{ namespace or "rcrai" }}
spec:
  rules:
  - host: {{ hostname }}
    http:
      paths:
      # 基于入口为基准的ingress规则, backend 只存在一个.
      - backend:
          serviceName: {{ serviceName }}
          servicePort: {{ servicePort or 80 }}
        path: {{ path }}
        pathType: ImplementationSpecific
  {% if tls is true %}
  tls:
  - hosts:
    - {{ hostname }}
    secretName: {{ secretName or "rcrai-tls" }}
  {% endif %}
{% endblock %}
