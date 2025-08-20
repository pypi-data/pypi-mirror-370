r'''
# cdk8s-jenkins

`cdk8s-jenkins` is a library that lets you easily define a manifest for deploying a Jenkins instance to your Kubernetes cluster.

## Prerequisites

This library uses a Custom Resource Definition provided by jenkins, and thus requires both the CRD and the operator to be installed on the cluster.
You can set this up by,

1. Apply the Custom Resource Definition(CRD) for jenkins on your Kubernetes cluster.

```
kubectl apply -f https://raw.githubusercontent.com/jenkinsci/kubernetes-operator/master/config/crd/bases/jenkins.io_jenkins.yaml
```

1. Install the Jenkins Operator on your Kubernetes cluster.

```
kubectl apply -f https://raw.githubusercontent.com/jenkinsci/kubernetes-operator/master/deploy/all-in-one-v1alpha2.yaml
```

> For more information regarding applying jenkins crd and installing jenkins operator, please refer [jenkins official documentaion](https://jenkinsci.github.io/kubernetes-operator/docs/getting-started/latest/installing-the-operator/).

## Usage

The library provides a high level `Jenkins` construct to provision a Jenkins instance.
You can just instantiate the Jenkins instance and that would add a Jenkins resource to the kubernetes manifest.

The library provide a set of defaults, so provisioning a basic Jenkins instance requires no configuration:

```python
import { Jenkins } from 'cdk8s-jenkins';

// inside your chart:
const jenkins = new Jenkins(this, 'my-jenkins');
```

The library also enables configuring the following parmeters for the Jenkins instance:

### metadata

```python
const jenkins = new Jenkins(this, 'my-jenkins', {
  metadata: {
    namespace: 'jenkins-namespace',
    labels: { customApp: 'my-jenkins' },
  },
});
```

### disableCsrfProtection

This allows you to toggle CSRF Protection for Jenkins.

```python
const jenkins = new Jenkins(this, 'my-jenkins', {
  disableCsrfProtection: true,
});
```

### basePlugins

These are the plugins required by the jenkins operator.

```python
const jenkins = new Jenkins(this, 'my-jenkins', {
  basePlugins: [{
    name: 'configuration-as-code',
    version: '1.55',
    }],
});
```

You can also utilize `addBasePlugins` function to add base plugins to jenkins configuration after initialization.

```python
const jenkins = new Jenkins(this, 'my-jenkins');
jenkins.addBasePlugins([{
  name: 'workflow-api',
  version: '2.76',
}]);
```

### plugins

These are the plugins that you can add to your jenkins instance.

```python
const jenkins = new Jenkins(this, 'my-jenkins', {
  plugins: [{
    name: 'simple-theme-plugin',
    version: '0.7',
    }],
});
```

You can also utilize `addPlugins` function to add plugins to jenkins configuration after initialization.

```python
const jenkins = new Jenkins(this, 'my-jenkins');
jenkins.addPlugins([{
  name: 'simple-theme-plugin',
  version: '0.7',
}]);
```

### seedJobs

You can define list of jenkins seed job configurations here. For more info you can take look at [jenkins documentation](https://jenkinsci.github.io/kubernetes-operator/docs/getting-started/latest/configuring-seed-jobs-and-pipelines/).

```python
const jenkins = new Jenkins(this, 'my-jenkins', {
  seedJobs: [{
    id: 'jenkins-operator',
    targets: 'cicd/jobs/*.jenkins',
    description: 'Jenkins Operator repository',
    repositoryBranch: 'master',
    repositoryUrl: 'https://github.com/jenkinsci/kubernetes-operator.git',
    }],
});
```

You can also utilize `addSeedJobs` function to add seed jobs to jenkins configuration after initialization.

```python
const jenkins = new Jenkins(this, 'my-jenkins');
jenkins.addSeedJobs([{
  id: 'jenkins-operator',
  targets: 'cicd/jobs/*.jenkins',
  description: 'Jenkins Operator repository',
  repositoryBranch: 'master',
  repositoryUrl: 'https://github.com/jenkinsci/kubernetes-operator.git',
}]);
```

## Using escape hatches

You can utilize escape hatches to make changes to the configurations that are not yet exposed by the library.

For instance, if you would like to update the version of a base plugin:

```python
const jenkins = new Jenkins(this, 'my-jenkins');
const jenkinsApiObject = ApiObject.of(jenkins);
jenkinsApiObject.addJsonPatch(JsonPatch.replace('/spec/master/basePlugins/1', {
  name: 'workflow-job',
  version: '3.00',
}));
```

For more information regarding escape hatches, take a look at [cdk8s documentation](https://cdk8s.io/docs/latest/concepts/escape-hatches/).

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more
information.

## License

This project is licensed under the Apache-2.0 License.
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import cdk8s as _cdk8s_d3d9af27
import constructs as _constructs_77d1e7e8


class Jenkins(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-jenkins.Jenkins",
):
    '''A jenkins instance.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        base_plugins: typing.Optional[typing.Sequence[typing.Union["Plugin", typing.Dict[builtins.str, typing.Any]]]] = None,
        disable_csrf_protection: typing.Optional[builtins.bool] = None,
        metadata: typing.Optional[typing.Union[_cdk8s_d3d9af27.ApiObjectMetadata, typing.Dict[builtins.str, typing.Any]]] = None,
        plugins: typing.Optional[typing.Sequence[typing.Union["Plugin", typing.Dict[builtins.str, typing.Any]]]] = None,
        seed_jobs: typing.Optional[typing.Sequence[typing.Union["SeedJob", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param base_plugins: List of plugins required by Jenkins operator. Default: - Default base plugins:: { name: 'kubernetes', version: '1.31.3' }, { name: 'workflow-job', version: '1145.v7f2433caa07f' }, { name: 'workflow-aggregator', version: '2.6' }, { name: 'git', version: '4.10.3' }, { name: 'job-dsl', version: '1.78.1' }, { name: 'configuration-as-code', version: '1414.v878271fc496f' }, { name: 'kubernetes-credentials-provider', version: '0.20' }
        :param disable_csrf_protection: Toggle for CSRF Protection on Jenkins resource. Default: - false
        :param metadata: Metadata associated with Jenkins resource. Default: : Default metadata values: { name: An app-unique name generated by the chart, annotations: No annotations, labels: { app: 'jenkins' }, namespace: default, finalizers: No finalizers, ownerReferences: Automatically set by Kubernetes }
        :param plugins: List of custom plugins applied to Jenkins resource. Default: - []
        :param seed_jobs: List of seed job configuration for Jenkins resource. For more information about seed jobs, please take a look at { Default: - No seed jobs
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72446e34172d3900118a01d2f5e7fe405c06fd092747e126f4819104c9f6d7d3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = JenkinsProps(
            base_plugins=base_plugins,
            disable_csrf_protection=disable_csrf_protection,
            metadata=metadata,
            plugins=plugins,
            seed_jobs=seed_jobs,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addBasePlugins")
    def add_base_plugins(self, *base_plugins: "Plugin") -> None:
        '''Add base plugins to jenkins instance.

        :param base_plugins: List of base plugins.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edc4fd6cb9750a65e94c6c1c74a03d3e5465f85379bd8321d629a5047bead71d)
            check_type(argname="argument base_plugins", value=base_plugins, expected_type=typing.Tuple[type_hints["base_plugins"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(None, jsii.invoke(self, "addBasePlugins", [*base_plugins]))

    @jsii.member(jsii_name="addPlugins")
    def add_plugins(self, *plugins: "Plugin") -> None:
        '''Add custom plugins to jenkins instance.

        :param plugins: List of custom plugins.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a208fc11ec0b64c7c29ad72d3b747209215402bf303d0e87f9a1c27deabd6dd)
            check_type(argname="argument plugins", value=plugins, expected_type=typing.Tuple[type_hints["plugins"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(None, jsii.invoke(self, "addPlugins", [*plugins]))

    @jsii.member(jsii_name="addSeedJobs")
    def add_seed_jobs(self, *seed_jobs: "SeedJob") -> None:
        '''Add seed jobs to jenkins instance.

        :param seed_jobs: List of seed jobs.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37b0c91af96e55de36855241220aef3530626841a1131387d44e140e073c145d)
            check_type(argname="argument seed_jobs", value=seed_jobs, expected_type=typing.Tuple[type_hints["seed_jobs"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(None, jsii.invoke(self, "addSeedJobs", [*seed_jobs]))


@jsii.data_type(
    jsii_type="cdk8s-jenkins.JenkinsProps",
    jsii_struct_bases=[],
    name_mapping={
        "base_plugins": "basePlugins",
        "disable_csrf_protection": "disableCsrfProtection",
        "metadata": "metadata",
        "plugins": "plugins",
        "seed_jobs": "seedJobs",
    },
)
class JenkinsProps:
    def __init__(
        self,
        *,
        base_plugins: typing.Optional[typing.Sequence[typing.Union["Plugin", typing.Dict[builtins.str, typing.Any]]]] = None,
        disable_csrf_protection: typing.Optional[builtins.bool] = None,
        metadata: typing.Optional[typing.Union[_cdk8s_d3d9af27.ApiObjectMetadata, typing.Dict[builtins.str, typing.Any]]] = None,
        plugins: typing.Optional[typing.Sequence[typing.Union["Plugin", typing.Dict[builtins.str, typing.Any]]]] = None,
        seed_jobs: typing.Optional[typing.Sequence[typing.Union["SeedJob", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Props for ``Jenkins``.

        :param base_plugins: List of plugins required by Jenkins operator. Default: - Default base plugins:: { name: 'kubernetes', version: '1.31.3' }, { name: 'workflow-job', version: '1145.v7f2433caa07f' }, { name: 'workflow-aggregator', version: '2.6' }, { name: 'git', version: '4.10.3' }, { name: 'job-dsl', version: '1.78.1' }, { name: 'configuration-as-code', version: '1414.v878271fc496f' }, { name: 'kubernetes-credentials-provider', version: '0.20' }
        :param disable_csrf_protection: Toggle for CSRF Protection on Jenkins resource. Default: - false
        :param metadata: Metadata associated with Jenkins resource. Default: : Default metadata values: { name: An app-unique name generated by the chart, annotations: No annotations, labels: { app: 'jenkins' }, namespace: default, finalizers: No finalizers, ownerReferences: Automatically set by Kubernetes }
        :param plugins: List of custom plugins applied to Jenkins resource. Default: - []
        :param seed_jobs: List of seed job configuration for Jenkins resource. For more information about seed jobs, please take a look at { Default: - No seed jobs
        '''
        if isinstance(metadata, dict):
            metadata = _cdk8s_d3d9af27.ApiObjectMetadata(**metadata)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a459058700d681813edb30fad5bba411efe07ec08e129aedf47aceff4bc7536)
            check_type(argname="argument base_plugins", value=base_plugins, expected_type=type_hints["base_plugins"])
            check_type(argname="argument disable_csrf_protection", value=disable_csrf_protection, expected_type=type_hints["disable_csrf_protection"])
            check_type(argname="argument metadata", value=metadata, expected_type=type_hints["metadata"])
            check_type(argname="argument plugins", value=plugins, expected_type=type_hints["plugins"])
            check_type(argname="argument seed_jobs", value=seed_jobs, expected_type=type_hints["seed_jobs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if base_plugins is not None:
            self._values["base_plugins"] = base_plugins
        if disable_csrf_protection is not None:
            self._values["disable_csrf_protection"] = disable_csrf_protection
        if metadata is not None:
            self._values["metadata"] = metadata
        if plugins is not None:
            self._values["plugins"] = plugins
        if seed_jobs is not None:
            self._values["seed_jobs"] = seed_jobs

    @builtins.property
    def base_plugins(self) -> typing.Optional[typing.List["Plugin"]]:
        '''List of plugins required by Jenkins operator.

        :default:

        - Default base plugins::

        { name: 'kubernetes', version: '1.31.3' },
        { name: 'workflow-job', version: '1145.v7f2433caa07f' },
        { name: 'workflow-aggregator', version: '2.6' },
        { name: 'git', version: '4.10.3' },
        { name: 'job-dsl', version: '1.78.1' },
        { name: 'configuration-as-code', version: '1414.v878271fc496f' },
        { name: 'kubernetes-credentials-provider', version: '0.20' }
        '''
        result = self._values.get("base_plugins")
        return typing.cast(typing.Optional[typing.List["Plugin"]], result)

    @builtins.property
    def disable_csrf_protection(self) -> typing.Optional[builtins.bool]:
        '''Toggle for CSRF Protection on Jenkins resource.

        :default: - false
        '''
        result = self._values.get("disable_csrf_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def metadata(self) -> typing.Optional[_cdk8s_d3d9af27.ApiObjectMetadata]:
        '''Metadata associated with Jenkins resource.

        :default:

        : Default metadata values:
        {
        name: An app-unique name generated by the chart,
        annotations: No annotations,
        labels: { app: 'jenkins' },
        namespace: default,
        finalizers: No finalizers,
        ownerReferences: Automatically set by Kubernetes
        }
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[_cdk8s_d3d9af27.ApiObjectMetadata], result)

    @builtins.property
    def plugins(self) -> typing.Optional[typing.List["Plugin"]]:
        '''List of custom plugins applied to Jenkins resource.

        :default: - []
        '''
        result = self._values.get("plugins")
        return typing.cast(typing.Optional[typing.List["Plugin"]], result)

    @builtins.property
    def seed_jobs(self) -> typing.Optional[typing.List["SeedJob"]]:
        '''List of seed job configuration for Jenkins resource.

        For more information about seed jobs, please take a look at {

        :default: - No seed jobs

        :link: https://github.com/jenkinsci/job-dsl-plugin/wiki/Tutorial---Using-the-Jenkins-Job-DSL Jenkins Seed Jobs Documentation }.
        '''
        result = self._values.get("seed_jobs")
        return typing.cast(typing.Optional[typing.List["SeedJob"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JenkinsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-jenkins.Plugin",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "version": "version", "download_url": "downloadUrl"},
)
class Plugin:
    def __init__(
        self,
        *,
        name: builtins.str,
        version: builtins.str,
        download_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Jenkins plugin.

        :param name: The name of Jenkins plugin.
        :param version: The version of Jenkins plugin.
        :param download_url: The url from where plugin has to be downloaded. Default: - Plugins are downloaded from Jenkins Update Centers.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51f7089b5b7f7938f285f2c97238625261f191e9c733e268baab733d8d38d1b5)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument download_url", value=download_url, expected_type=type_hints["download_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "version": version,
        }
        if download_url is not None:
            self._values["download_url"] = download_url

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of Jenkins plugin.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''The version of Jenkins plugin.'''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def download_url(self) -> typing.Optional[builtins.str]:
        '''The url from where plugin has to be downloaded.

        :default: - Plugins are downloaded from Jenkins Update Centers.

        :see: https://github.com/jenkinsci/kubernetes-operator/blob/master/pkg/configuration/base/resources/scripts_configmap.go#L121-L124
        '''
        result = self._values.get("download_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Plugin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-jenkins.SeedJob",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "id": "id",
        "repository_branch": "repositoryBranch",
        "repository_url": "repositoryUrl",
        "targets": "targets",
    },
)
class SeedJob:
    def __init__(
        self,
        *,
        description: builtins.str,
        id: builtins.str,
        repository_branch: builtins.str,
        repository_url: builtins.str,
        targets: builtins.str,
    ) -> None:
        '''Jenkins seed job.

        :param description: The description of the seed job.
        :param id: The unique name for the seed job.
        :param repository_branch: The repository branch where seed job definitions are present.
        :param repository_url: The repository access URL. Supports SSH and HTTPS.
        :param targets: The repository path where seed job definitions are present.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f95ca97b71e9b5886de21dc226c0666de7cd25c282df40f4d7b760c008fd659e)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument repository_branch", value=repository_branch, expected_type=type_hints["repository_branch"])
            check_type(argname="argument repository_url", value=repository_url, expected_type=type_hints["repository_url"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "description": description,
            "id": id,
            "repository_branch": repository_branch,
            "repository_url": repository_url,
            "targets": targets,
        }

    @builtins.property
    def description(self) -> builtins.str:
        '''The description of the seed job.'''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> builtins.str:
        '''The unique name for the seed job.'''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_branch(self) -> builtins.str:
        '''The repository branch where seed job definitions are present.'''
        result = self._values.get("repository_branch")
        assert result is not None, "Required property 'repository_branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_url(self) -> builtins.str:
        '''The repository access URL.

        Supports SSH and HTTPS.
        '''
        result = self._values.get("repository_url")
        assert result is not None, "Required property 'repository_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def targets(self) -> builtins.str:
        '''The repository path where seed job definitions are present.'''
        result = self._values.get("targets")
        assert result is not None, "Required property 'targets' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SeedJob(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Jenkins",
    "JenkinsProps",
    "Plugin",
    "SeedJob",
]

publication.publish()

def _typecheckingstub__72446e34172d3900118a01d2f5e7fe405c06fd092747e126f4819104c9f6d7d3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    base_plugins: typing.Optional[typing.Sequence[typing.Union[Plugin, typing.Dict[builtins.str, typing.Any]]]] = None,
    disable_csrf_protection: typing.Optional[builtins.bool] = None,
    metadata: typing.Optional[typing.Union[_cdk8s_d3d9af27.ApiObjectMetadata, typing.Dict[builtins.str, typing.Any]]] = None,
    plugins: typing.Optional[typing.Sequence[typing.Union[Plugin, typing.Dict[builtins.str, typing.Any]]]] = None,
    seed_jobs: typing.Optional[typing.Sequence[typing.Union[SeedJob, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edc4fd6cb9750a65e94c6c1c74a03d3e5465f85379bd8321d629a5047bead71d(
    *base_plugins: Plugin,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a208fc11ec0b64c7c29ad72d3b747209215402bf303d0e87f9a1c27deabd6dd(
    *plugins: Plugin,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37b0c91af96e55de36855241220aef3530626841a1131387d44e140e073c145d(
    *seed_jobs: SeedJob,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a459058700d681813edb30fad5bba411efe07ec08e129aedf47aceff4bc7536(
    *,
    base_plugins: typing.Optional[typing.Sequence[typing.Union[Plugin, typing.Dict[builtins.str, typing.Any]]]] = None,
    disable_csrf_protection: typing.Optional[builtins.bool] = None,
    metadata: typing.Optional[typing.Union[_cdk8s_d3d9af27.ApiObjectMetadata, typing.Dict[builtins.str, typing.Any]]] = None,
    plugins: typing.Optional[typing.Sequence[typing.Union[Plugin, typing.Dict[builtins.str, typing.Any]]]] = None,
    seed_jobs: typing.Optional[typing.Sequence[typing.Union[SeedJob, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51f7089b5b7f7938f285f2c97238625261f191e9c733e268baab733d8d38d1b5(
    *,
    name: builtins.str,
    version: builtins.str,
    download_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f95ca97b71e9b5886de21dc226c0666de7cd25c282df40f4d7b760c008fd659e(
    *,
    description: builtins.str,
    id: builtins.str,
    repository_branch: builtins.str,
    repository_url: builtins.str,
    targets: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
