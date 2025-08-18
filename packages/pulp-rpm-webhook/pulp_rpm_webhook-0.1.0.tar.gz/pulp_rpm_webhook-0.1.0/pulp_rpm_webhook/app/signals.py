import logging
from .webhook import send_webhook

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from pulpcore.app.models import (
  RepositoryContent,
  ContentArtifact,
  RemoteArtifact,
)
from pulp_rpm.app.models import (
  RpmPublication,
  RpmDistribution,
  Package as RpmPackage,
)

logger = logging.getLogger(__name__)
logger.debug("Module loaded: RPM Webhook")

#
# Translate relative path to actual path of the rpm in distribution
#
def published_relpath(pkg) -> str:
  """Return the path as it will appear under the distribution root."""
  loc = (getattr(pkg, "location_href", "") or "").lstrip("/")
  # If sync provided a full path already (e.g. "Packages/p/foo.rpm"), keep it.
  if loc.startswith("Packages/") or "/" in loc:
    return loc

  # Otherwise (typical for uploads), build the filename and the Packages/<first-letter>/ layout
  fname = loc or f"{pkg.name}-{pkg.version}-{pkg.release}.{pkg.arch}.rpm"
  first = (fname[0].lower() if fname else "_")
  return f"Packages/{first}/{fname}"

#
# Catch RPM publication signal and forward RPM info to webhook
#
@receiver(post_save, sender=RpmPublication)
def on_rpm_publication_created(sender, instance: RpmPublication, created: bool, **kwargs):
  if not created:
    return

  rv = instance.repository_version
  repo = rv.repository
  content_origin = (getattr(settings, "CONTENT_ORIGIN", "") or "").rstrip("/")

  # Prefer distributions bound to this publication
  # Worst case scenario any distribution serving this repo
  dists = list(RpmDistribution.objects.filter(publication=instance)) or \
          list(RpmDistribution.objects.filter(repository=repo))

  # RPMs added in this version
  added_rc = RepositoryContent.objects.filter(
    repository=repo, version_added=rv
  ).only("content_id")
  pkg_pks = [rc.content_id for rc in added_rc]

  # Bulk fetch packages
  pk_to_pkg = {p.pk: p for p in RpmPackage.objects.filter(pk__in=pkg_pks)}

  # Map content_id -> content_artifact_pk
  ca_rows = ContentArtifact.objects.filter(content_id__in=pkg_pks) \
                                    .values_list("pk", "content_id")
  content_id_to_ca_pk = {content_id: ca_pk for (ca_pk, content_id) in ca_rows}
  ca_pks = list(content_id_to_ca_pk.values())

  # Map content_artifact_pk -> upstream url
  ra_rows = RemoteArtifact.objects.filter(content_artifact_id__in=ca_pks) \
                                  .values("content_artifact_id", "url")
  ca_pk_to_upstream = {row["content_artifact_id"]: row["url"] for row in ra_rows}

  packages = []
  for pk, pkg in pk_to_pkg.items():
    distribution_urls = []
    if content_origin and dists:
      rel = published_relpath(pkg)

      for dist in dists:
        base_path = (dist.base_path or "").strip("/")
        distribution_urls.append(f"{content_origin}/pulp/content/{base_path}/{rel}")

    # upstream URL (if synced from a Remote)
    upstream_url = None
    ca_pk = content_id_to_ca_pk.get(pk)
    if ca_pk:
      upstream_url = ca_pk_to_upstream.get(ca_pk)

    # Add package only if it contains distribution URL
    if distribution_urls:
      packages.append({
        "name": pkg.name,
        "epoch": pkg.epoch,
        "version": pkg.version,
        "release": pkg.release,
        "arch": pkg.arch,
        "location_href": pkg.location_href,
        "distribution_urls": distribution_urls,  # public download URLs if any Distribution exists
        "upstream_url": upstream_url,            # where Pulp would fetch from (None for uploads)
      })

  payload = {
    "event": "rpm.published",
    "repository": repo.name,
    "publication": {
      "distribution_roots": [
        f"{content_origin}/pulp/content/{(d.base_path or '').strip('/')}/"
        for d in dists
      ] if (content_origin and dists) else [],
    },
    "packages_added": packages,
  }

  if packages:
    logger.debug(f"Payload: {payload}")
    send_webhook(payload)
