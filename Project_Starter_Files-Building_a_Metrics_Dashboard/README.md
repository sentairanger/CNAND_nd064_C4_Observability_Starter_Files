**Note:** For the screenshots, you can store all of your answer images in the `answer-img` directory.

## Verify the monitoring installation

*TODO:* run `kubectl` command to show the running pods and services for all components. Take a screenshot of the output and include it here to verify the installation

To install grafana/prometheus, use these commands:

First make sure you have vagrant installed. I didn't and I used Kind/Kubectl to run my application. If you are going to use vagrant run these commands.

```
vagrant up
vagrant ssh
kubectl version
```
Second, install helm
`curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash`

Next, create a namespace called monitoring by using this command:

`kubectl create ns observability`

Then run these commands to install prometheus/grafana. Note I was using kubectl/kind so I had to change the config file name to ~/.kube/config. 

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
# helm repo add stable https://kubernetes-charts.storage.googleapis.com # this is deprecated
helm repo add stable https://charts.helm.sh/stable
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --kubeconfig /etc/rancher/k3s/k3s.yaml
```
Port forward with the following:

`kubectl port-forward service/prometheus-grafana --address 0.0.0.0 3000:80 -n monitoring`

Then login with user admin and password prom-operator. Please change this as this is not secure.

To install Jaeger, I followed a different method. I ran these commands instead:

First create a namespace called observability:

`kubectl create ns observability`

Next, run these commands: 

```
##.if crd not exist: kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/crds/jaegertracing.io_jaegers_crd.yaml 
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts  
helm repo update 
helm install jaeger jaegertracing/jaeger-operator --namespace observability --set rbac.clusterRole=true 
```

Then make sure you expand cluster wide permissions:

```
# cluster_role.yaml
kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/cluster_role.yaml
# cluster_role_binding.yaml
kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/cluster_role_binding.yaml
```
Add an ingress to the cluster:

`kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.0.3/deploy/static/provider/cloud/deploy.yaml`

Next, if not done yet, add a Jaeger instance with:

```
cat <<EOF | kubectl apply -f -
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: simplest
EOF
```

And it should appear. Then make sure to get the FQDN of the query to add it as a data source on Grafana. And then make sure to alter the backend.yaml file to ensure that it uses the correct agent under JAEGER_HOST.

To run the app just go to the manifests directory and run `kubectl apply -f app/`. However, if you want to do each one individually just run `kubectl apply -f app/backend.yaml` for example.


[Monitoring Deployments](https://github.com/sentairanger/CNAND_nd064_C4_Observability_Starter_Files/blob/master/Project_Starter_Files-Building_a_Metrics_Dashboard/answer-img/monitoring_deployments.png)
[Monitoring Services](https://github.com/sentairanger/CNAND_nd064_C4_Observability_Starter_Files/blob/master/Project_Starter_Files-Building_a_Metrics_Dashboard/answer-img/monitoring_svcs.png)
[Monitoring Pods](https://github.com/sentairanger/CNAND_nd064_C4_Observability_Starter_Files/blob/master/Project_Starter_Files-Building_a_Metrics_Dashboard/answer-img/monitoring_pods.png)
[Observability Deployments](https://github.com/sentairanger/CNAND_nd064_C4_Observability_Starter_Files/blob/master/Project_Starter_Files-Building_a_Metrics_Dashboard/answer-img/observability_deploy.png)
[Observability Services](https://github.com/sentairanger/CNAND_nd064_C4_Observability_Starter_Files/blob/master/Project_Starter_Files-Building_a_Metrics_Dashboard/answer-img/observability_svc.png)
[Observability Pods](https://github.com/sentairanger/CNAND_nd064_C4_Observability_Starter_Files/blob/master/Project_Starter_Files-Building_a_Metrics_Dashboard/answer-img/observability_pod.png)
[Default Deployments](https://github.com/sentairanger/CNAND_nd064_C4_Observability_Starter_Files/blob/master/Project_Starter_Files-Building_a_Metrics_Dashboard/answer-img/default-deploy.png)
[Default Services](https://github.com/sentairanger/CNAND_nd064_C4_Observability_Starter_Files/blob/master/Project_Starter_Files-Building_a_Metrics_Dashboard/answer-img/default-svc.png)
[Default Pods](https://github.com/sentairanger/CNAND_nd064_C4_Observability_Starter_Files/blob/master/Project_Starter_Files-Building_a_Metrics_Dashboard/answer-img/default-pods.png)

## Setup the Jaeger and Prometheus source
*TODO:* Expose Grafana to the internet and then setup Prometheus as a data source. Provide a screenshot of the home page after logging into Grafana.

[Grafana Homepage](https://github.com/sentairanger/CNAND_nd064_C4_Observability_Starter_Files/blob/master/Project_Starter_Files-Building_a_Metrics_Dashboard/answer-img/grafana_homepage.png)

[Prometheus Data](https://github.com/sentairanger/CNAND_nd064_C4_Observability_Starter_Files/blob/master/Project_Starter_Files-Building_a_Metrics_Dashboard/answer-img/grafana_prometheus_data.png)

## Create a Basic Dashboard
*TODO:* Create a dashboard in Grafana that shows Prometheus as a source. Take a screenshot and include it here.

[Basic Dashboard](https://github.com/sentairanger/CNAND_nd064_C4_Observability_Starter_Files/blob/master/Project_Starter_Files-Building_a_Metrics_Dashboard/answer-img/basic_grafana_dashboard.png)


## Describe SLO/SLI
*TODO:* Describe, in your own words, what the SLIs are, based on an SLO of *monthly uptime* and *request response time*.

SLIs are metrics that are used to measure performance of any application. SLOs are goals that can be measured to set a standard of performance. For example one day there can be an SLO of 99.99 percent while the next day we might see an SLO of 99.95 percent. Of course there is always that elusive goal of hitting what is known as the five nines of uptime.

## Creating SLI metrics.
*TODO:* It is important to know why we want to measure certain metrics for our customer. Describe in detail 5 metrics to measure these SLIs. 

1. Latency: The time a service takes to complete a request (usually measured in milliseconds)
2. Resource Saturation: The overall capacity of resources such as CPU and RAM
3. Traffic: The amount of stress on a system, for example HTTP requests per second.
4. Errors: The amount of failing requests which can be 4xx and 5xx HTTP errors. (represented in percentage)
5. Uptime: The percentage of time in which a service is up and running. Example, pod uptime would be at less than or equal to 99.99 percent. 

## Create a Dashboard to measure our SLIs
*TODO:* Create a dashboard to measure the uptime of the frontend and backend services We will also want to measure to measure 40x and 50x errors. Create a dashboard that show these values over a 24 hour period and take a screenshot.
[First Dashboard](https://github.com/sentairanger/CNAND_nd064_C4_Observability_Starter_Files/blob/master/Project_Starter_Files-Building_a_Metrics_Dashboard/answer-img/project-dashboard.png)


## Tracing our Flask App
*TODO:*  We will create a Jaeger span to measure the processes on the backend. Once you fill in the span, provide a screenshot of it here.
[Jaeger Trace](https://github.com/sentairanger/CNAND_nd064_C4_Observability_Starter_Files/blob/master/Project_Starter_Files-Building_a_Metrics_Dashboard/answer-img/jaeger-span.png)

## Jaeger in Dashboards
*TODO:* Now that the trace is running, let's add the metric to our current Grafana dashboard. Once this is completed, provide a screenshot of it here.
[Jaeger Grafana](https://github.com/sentairanger/CNAND_nd064_C4_Observability_Starter_Files/blob/master/Project_Starter_Files-Building_a_Metrics_Dashboard/answer-img/jaeger-grafana.png)

## Report Error
*TODO:* Using the template below, write a trouble ticket for the developers, to explain the errors that you are seeing (400, 500, latency) and to let them know the file that is causing the issue.

TROUBLE TICKET

Name: Issue with /star, obtained 405 Method Not Allowed Error

Date: October 21, 2021 10:37pm

Subject: MongoDB that is required by the backend is not accessible 

Affected Area: Backend Service

Severity: High

Description: When port-forwarding the application for testing it turns out that the 405 error came up when accessing /star. I've isolated the issue to the mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb link that does not exist in the cluster. For this to work, the MongoDB link must be made available in the cluster.

## Creating SLIs and SLOs
*TODO:* We want to create an SLO guaranteeing that our application has a 99.95% uptime per month. Name three SLIs that you would use to measure the success of this SLO.

1. Error Rate: We want to ensure that the 2xx rates are at around 97%.
2. Uptime: We want uptime to be at x<=99 percent within a month and response time should be at about 500 milliseconds for a request at 99.99 percent but ideally we want to hit the five nines.
3. Latency: Requests should take less than 30ms overall in the month.

## Building KPIs for our plan
*TODO*: Now that we have our SLIs and SLOs, create KPIs to accurately measure these metrics. We will make a dashboard for this, but first write them down here.
1. Error rate (errors per second and response rate per second)
2. Uptime
3. Traffic (successful requests per second/ requests per second)
4. Latency (response time)
5. Resource Usage (CPU, RAM usage)

## Final Dashboard
*TODO*: Create a Dashboard containing graphs that capture all the metrics of your KPIs and adequately representing your SLIs and SLOs. Include a screenshot of the dashboard here, and write a text description of what graphs are represented in the dashboard.  
[Final Dashboard 1](https://github.com/sentairanger/CNAND_nd064_C4_Observability_Starter_Files/blob/master/Project_Starter_Files-Building_a_Metrics_Dashboard/answer-img/Final-Dashboard-One.png)
[Final Dashboard 2](https://github.com/sentairanger/CNAND_nd064_C4_Observability_Starter_Files/blob/master/Project_Starter_Files-Building_a_Metrics_Dashboard/answer-img/Final-Dashboard-Two.png)

1. Jaeger Spans (Tracing of the Backend Service using Jaeger)
2. Requests Per Second (number of requests per second)
3. RAM Usage Per Pod (Amount of RAM being used by each pod)
4. Total Requests per second (The amount of requests per second)
5. CPU Usage Per Pod (The Amount of CPU being used per pod)
6. 4xx and 5xx failed Requests per second (the amount of failed requests per second)
7. Average Error Rage (the average error rate per second)
8. Average Response Time (The average HTTP response time)
9. Pod Uptime (Uptime of each pod)
