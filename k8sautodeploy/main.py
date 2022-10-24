# 这是一个示例 Python 脚本。
from jinja2 import Template
import jinja2.exceptions
import os
import sys
import yaml
from pathlib import Path
from utils.convert import convert
from utils.rollingUpdate import rollingUpdate


def get_config():
    config_file = os.path.dirname(os.path.realpath(__file__)) + "/etc/config.yaml"
    try:
        cfg = yaml.safe_load(open(config_file, "r", encoding="utf-8").read())
        cfg_obj = obj_dic(cfg)
    except yaml.parser.ParserError as ParserError:
        print('yaml.parser.ParserError: %s' % ParserError)
        sys.exit(1)

    return cfg_obj


def obj_dic(cfg):
    top = type("new", (object,), cfg)
    seqs = tuple, set, frozenset
    for i, j in cfg.items():
        if isinstance(j, dict):
            if i == 'resources':
                setattr(top, i, j)
            else:
                setattr(top, i, obj_dic(j))
        elif isinstance(j, seqs):
            setattr(top, i, type(j)(obj_dic(sj) if isinstance(sj, dict) else sj for sj in j))
        else:
            setattr(top, i, j)
    return top


def try_open_template(template_path):
    try:
        with template_path.open(encoding="utf-8") as f:
            tpl = Template(f.read())
    except jinja2.exceptions.TemplateAssertionError as TemplateAssertionError:
        print(
            "jinja2.exceptions.TemplateAssertionError: %s,\n"
            "请将jinja2 至少升级至3.0.3 "
            "或执行pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple/  -r requirements.txt" % TemplateAssertionError)
        sys.exit(1)
    except jinja2.exceptions.TemplateSyntaxError as TemplateSyntaxError:
        print("jinja2.exceptions.TemplateSyntaxError: %s" % TemplateSyntaxError)
        sys.exit(1)
    except jinja2.exceptions.TemplateNotFound as TemplateNotFound:
        print("jinja2.exceptions.TemplateNotFound: %s " % TemplateNotFound)
        sys.exit(1)
    except jinja2.exceptions.UndefinedError as Undefined:
        print("jinja2.exceptions.Undefined: %s" % Undefined)
        sys.exit(1)
    return tpl


class Generator(object):
    def __init__(self):
        self.cfg = get_config()
        self.name = self.cfg.app.name
        self.namespace = self.cfg.namespace
        self.service = self.cfg.service
        self.ingress = self.cfg.ingress
        self.containerPorts = self.cfg.containerPorts
        self.replicaCount = self.cfg.replicaCount
        self.image = self.cfg.image
        self.resources = self.cfg.resources
        self.metrics = self.cfg.metrics
        self.extraEnvVars = self.cfg.extraEnvVars
        self.livenessProbe = self.cfg.livenessProbe
        self.readinessProbe = self.cfg.readinessProbe
        self.staticSiteConfigmap = self.cfg.staticSiteConfigmap

    @staticmethod
    def get_ingress_metadata_name(hostname, path):
        string = "%s/%s" % (hostname, path)
        return convert(string)

    def create_ingress_file(self):
        if self.ingress.enabled is False:
            return

        for host in self.ingress.hosts:
            template_path = Path('templates/ingress.tpl')
            tpl = try_open_template(template_path)

            metadata_name = self.get_ingress_metadata_name(host['hostname'], host['path'])
            if metadata_name == '/':
                print("metadata.name 异常, 请检查后继续. ")
                sys.exit(1)

            ingress_config = tpl.render(
                hostname=host['hostname'],
                metadataName=metadata_name,
                namespace=self.namespace,
                serviceName=self.name,
                servicePort=80,
                path=host['path'],
                tls=host['tls'] if 'tls' in host else False,
                rewrite=host['rewrite'] if 'rewrite' in host else False,
                rewriteTargetPath=host['rewriteTargetPath'] if 'rewriteTargetPath' in host else None
            )
            config_path = 'target/ingress/%s-ingress.yaml' % metadata_name
            with open(config_path, 'w', encoding='utf-8') as fw:
                fw.write(ingress_config)

    def create_service_file(self):
        template_path = Path('templates/service.tpl')
        tpl = try_open_template(template_path)

        service_config = tpl.render(
            namespace=self.namespace,
            name=self.name,
            containerPort=self.containerPorts.http,
            grpc=self.service.grpc
        )
        config_path = 'target/service/%s-service.yaml' % self.name
        with open(config_path, 'w', encoding='utf-8') as fw:
            fw.write(service_config)

    def liveness_probe(self):
        if self.livenessProbe.enabled:
            livenessProbeConfig = {
                'enabled': self.livenessProbe.enabled,
                'httpGet': {
                    'path': self.livenessProbe.httpGet.path or '/healthz',
                    'port': self.livenessProbe.httpGet.port or '8080'
                },
                'initialDelaySeconds': self.livenessProbe.initialDelaySeconds or 30,
                'timeoutSeconds': self.livenessProbe.timeoutSeconds or 5,
                'periodSeconds': self.livenessProbe.periodSeconds or 10,
                'failureThreshold': self.livenessProbe.failureThreshold or 3,
                'successThreshold': self.livenessProbe.successThreshold or 1
            }
            return livenessProbeConfig
        else:
            return False

    def readiness_probe(self):
        if self.readinessProbe.enabled:
            readinessProbeConfig = {
                'enabled': self.readinessProbe.enabled,
                'httpGet': {
                    'path': self.readinessProbe.httpGet.path or '/healthz',
                    'port': self.readinessProbe.httpGet.port or '8080'
                },
                'initialDelaySeconds': self.readinessProbe.initialDelaySeconds or 30,
                'timeoutSeconds': self.readinessProbe.timeoutSeconds or 5,
                'periodSeconds': self.readinessProbe.periodSeconds or 10,
                'failureThreshold': self.readinessProbe.failureThreshold or 3,
                'successThreshold': self.readinessProbe.successThreshold or 1
            }
            return readinessProbeConfig
        else:
            return False

    def staticsite_configmap(self):
        if self.staticSiteConfigmap.enabled:
            config = []
            for c in self.staticSiteConfigmap.config:
                if 'mountPath' in c and 'configName' in c and c['mountPath'].split('/')[-1] == c['configName']:
                    c['mountPath'] = '/'.join(c['mountPath'].split('/')[:-1])
                config.append(c)
            staticSiteConfigmapConfig = {
                'enabled': self.staticSiteConfigmap.enabled,
                'config': config,
            }
            return staticSiteConfigmapConfig
        else:
            return False

    def create_deployment_file(self):
        template_path = Path('templates/deployment.tpl')
        tpl = try_open_template(template_path)

        template_path = Path('templates/deployment.tpl')
        tpl = try_open_template(template_path)

        deployment_config = tpl.render(
            namespace=self.namespace,
            name=self.name,
            replicaCount=self.replicaCount,
            maxSurge=rollingUpdate(self.replicaCount)['maxSurge'] if rollingUpdate(self.replicaCount) else 1,
            maxUnavailable=rollingUpdate(self.replicaCount)['maxUnavailable'] if rollingUpdate(
                self.replicaCount) else 0,
            imageRegistry=self.image.registry,
            imageNamespace=self.image.namespace,
            iamgeTag=self.image.tag,
            resources=self.resources,
            metricsEnabled=self.metrics.enabled,
            metricsPort=self.metrics.port,
            extraEnvVars=self.extraEnvVars,
            livenessProbe=self.liveness_probe(),
            readinessProbe=self.readiness_probe(),
            staticSiteConfigmap=self.staticsite_configmap()
        )
        config_path = 'target/deployment/%s-deployment.yaml' % self.name
        with open(config_path, 'w', encoding='utf-8') as fw:
            fw.write(deployment_config)


if __name__ == '__main__':
    g = Generator()
    g.create_ingress_file()
    g.create_service_file()
    g.create_deployment_file()

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
