const INSTANCE_ID = /^[a-z][a-z0-9-]{1,63}$/;

export function createInstanceScope(componentId, prefix, context = {}) {
  const instanceId = context.instanceId;
  if (typeof instanceId !== "string" || !INSTANCE_ID.test(instanceId)) {
    throw new Error(`[${componentId}] context.instanceId 必须匹配 ${INSTANCE_ID}`);
  }
  const rootId = `${instanceId}-${prefix}-root`;
  if (document.getElementById(rootId)) {
    throw new Error(`[${componentId}] instanceId 冲突: ${instanceId}`);
  }
  return { instanceId, prefix, rootId };
}

export function assignInstanceRoot(element, scope) {
  element.id = scope.rootId;
  element.dataset.instanceId = scope.instanceId;
  return element;
}

export function assertUniqueInstanceId(componentId, instanceId) {
  if (typeof instanceId !== "string" || !INSTANCE_ID.test(instanceId)) {
    throw new Error(`[${componentId}] context.instanceId 必须匹配 ${INSTANCE_ID}`);
  }
  if (document.querySelector?.(`[data-instance-id="${instanceId}"]`)) {
    throw new Error(`[${componentId}] instanceId 冲突: ${instanceId}`);
  }
  return instanceId;
}

export function assertProjectLocalMediaRef(componentId, mediaRef) {
  if (typeof mediaRef !== "string" || !mediaRef.trim()) {
    throw new Error(`[${componentId}] mediaRef 必须是项目本地相对路径`);
  }
  const value = mediaRef.trim().replaceAll("\\", "/");
  if (/^(?:[a-z]+:|\/\/|\/)/i.test(value) || value.split("/").includes("..")) {
    throw new Error(`[${componentId}] mediaRef 只能使用项目根内的相对路径`);
  }
  return value;
}
