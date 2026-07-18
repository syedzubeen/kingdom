// Keep CI placeholders literal when the examples are assembled as template strings.
const BUILD_NUMBER = '${BUILD_NUMBER}';
const artifacts = [
  {name:'Dockerfile', tag:'CONTAINERIZATION', desc:'A production-ready multi-stage image built from your application analysis.', code:`FROM golang:1.23 AS build\nWORKDIR /src\nCOPY go.mod go.sum* ./\nRUN go mod download\nCOPY . .\nRUN CGO_ENABLED=0 go build -o /out/app ./...\n\nFROM gcr.io/distroless/static-debian12:nonroot\nCOPY --from=build /out/app /app\nEXPOSE 8080\nENTRYPOINT ["/app"]`},
  {name:'docker-compose.yml', tag:'LOCAL DEVELOPMENT', desc:'A single-command local environment with your application wired to its dependencies.', code:`services:\n  sample-go-app:\n    build: .\n    ports:\n      - "8080:8080"\n    environment:\n      PORT: 8080`},
  {name:'.gitlab-ci.yml', tag:'CONTINUOUS INTEGRATION', desc:'Cached test and build stages that keep every merge request honest.', code:`stages: [test, build]\ncache:\n  paths: [go/pkg/mod]\n\ntest:\n  image: golang:1.23\n  script:\n    - go test ./...\n\nbuild:\n  image: docker:27\n  script:\n    - docker build -t $CI_REGISTRY_IMAGE .`},
  {name:'Jenkinsfile', tag:'CONTINUOUS DELIVERY', desc:'A declarative pipeline that tests the app and builds its image.', code:`pipeline {\n  agent any\n  stages {\n    stage('Test') {\n      steps { sh 'go test ./...' }\n    }\n    stage('Build') {\n      steps { sh 'docker build -t kingdom:${BUILD_NUMBER} .' }\n    }\n  }\n}`},
  {name:'Kubernetes', tag:'ORCHESTRATION', desc:'Deployment, service, config, and secret manifests ready for review.', code:`apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: sample-go-app\nspec:\n  replicas: 2\n  template:\n    spec:\n      containers:\n        - name: sample-go-app\n          image: sample-go-app:latest\n          ports:\n            - containerPort: 8080`},
  {name:'Terraform', tag:'INFRASTRUCTURE', desc:'Minimal Docker-host deployment infrastructure to get you moving.', code:`terraform {\n  required_version = ">= 1.5.0"\n}\n\nresource "docker_image" "app" {\n  name = "sample-go-app:latest"\n  build { context = ".." }\n}\n\nresource "docker_container" "app" {\n  name = "sample-go-app"\n  image = docker_image.app.image\n}`},
  {name:'DEPLOYMENT.md', tag:'DOCUMENTATION', desc:'A handoff guide with build, local run, deploy, and secret instructions.', code:`# Deployment guide\n\n## Local\nRun docker compose up --build.\n\n## Kubernetes\nReplace secret values, then apply the manifests.\n\n## Environment variables\nPORT, DB_HOST, JWT_SECRET`},
];

const $ = (selector) => document.querySelector(selector);
const tabs = $('#artifactTabs');
artifacts.forEach((artifact, index) => {
  const tab = document.createElement('button');
  tab.className = `artifact-tab ${index === 0 ? 'selected' : ''}`;
  tab.innerHTML = `<span>${artifact.name}</span><span class="tab-index">0${index + 1}</span>`;
  tab.addEventListener('click', () => selectArtifact(index));
  tabs.appendChild(tab);
});
const docsTab = document.createElement('button');
docsTab.className = 'artifact-tab docs-tab';
docsTab.innerHTML = '<span>Documentation</span><span class="tab-index">DOCS</span>';
docsTab.addEventListener('click', selectDocs);
tabs.appendChild(docsTab);
function selectArtifact(index) {
  const artifact = artifacts[index];
  document.querySelectorAll('.workspace-top, .artifact-meta, .code-window, .bottom-grid').forEach((element) => element.classList.remove('docs-hidden'));
  $('#docsPanel').classList.remove('visible');
  document.querySelectorAll('.artifact-tab').forEach((tab, i) => tab.classList.toggle('selected', i === index));
  $('#artifactTitle').textContent = artifact.name;
  $('#artifactTag').textContent = artifact.tag;
  $('#artifactDesc').textContent = artifact.desc;
  $('#fileName').textContent = artifact.name;
  $('#codePreview').textContent = artifact.code;
  $('#nextArtifact').textContent = artifacts[(index + 1) % artifacts.length].name;
}
function selectDocs() {
  document.querySelectorAll('.artifact-tab').forEach((tab) => tab.classList.remove('selected'));
  docsTab.classList.add('selected');
  document.querySelectorAll('.workspace-top, .artifact-meta, .code-window, .bottom-grid').forEach((element) => element.classList.add('docs-hidden'));
  $('#docsPanel').classList.add('visible');
}
selectArtifact(0);
$('#enterButton').addEventListener('click', () => { $('#landing').classList.add('leaving'); setTimeout(() => { $('#landing').style.display = 'none'; $('#app').classList.add('visible'); }, 720); });
$('#nextButton').addEventListener('click', () => selectArtifact((artifacts.findIndex(a => a.name === $('#nextArtifact').textContent) + artifacts.length) % artifacts.length));
$('#generateButton').addEventListener('click', () => { const button = $('#generateButton'); button.innerHTML = 'ANALYZING <span>◌</span>'; setTimeout(() => { button.innerHTML = 'GENERATE <span>↗</span>'; selectArtifact(0); showToast('Repository analyzed · artifacts ready'); }, 900); });
$('#copyButton').addEventListener('click', async () => { try { await navigator.clipboard.writeText($('#codePreview').textContent); } catch (_) {} showToast('Copied to clipboard'); });
$('#copyDocsCommand').addEventListener('click', async () => { try { await navigator.clipboard.writeText('kingdom ./your-go-app --output generated'); } catch (_) {} showToast('Quick start copied'); });
function showToast(message) { const toast = $('#toast'); toast.textContent = message; toast.classList.add('show'); setTimeout(() => toast.classList.remove('show'), 2200); }
