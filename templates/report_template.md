# GitHub Repository Analysis: {{ report.overview.metadata.full_name }}

> **Generated at:** {{ report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC') }}  
> **Analysis Duration:** {{ "%.2f"|format(report.duration_seconds) }}s  
> **Repository Health:** **{{ report.intelligence.health_status }}** ({{ report.intelligence.repository_health_score }}/100)

---

## Executive Summary

{{ report.intelligence.executive_summary }}

---

## 1. Repository Overview

| Property | Value |
| :--- | :--- |
| **Repository** | `{{ report.overview.metadata.full_name }}` |
| **Default Branch** | `{{ report.overview.metadata.default_branch }}` |
| **Stars** | {{ report.overview.metadata.stars_count }} |
| **Forks** | {{ report.overview.metadata.forks_count }} |
| **Open Issues / PRs** | {{ report.overview.metadata.open_issues_count }} |
| **License** | {{ report.overview.metadata.license_name or "Not detected" }} |
| **Primary Languages** | {{ report.overview.structure.languages | join(', ') if report.overview.structure.languages else "Unknown" }} |
| **Key Entry Points** | {{ report.overview.structure.entry_points | join(', ') if report.overview.structure.entry_points else "None detected" }} |
| **Config Manifests** | {{ report.overview.structure.manifest_files | join(', ') if report.overview.structure.manifest_files else "None" }} |
| **Docker Support** | {{ "Yes" if report.overview.structure.docker_present else "No" }} |
| **CI/CD Pipeline** | {{ "Yes" if report.overview.structure.ci_cd_present else "No" }} |

---

## 2. Issues Analysis

- **Total Issues Analyzed:** {{ report.issue_data.total_issues_analyzed }}
- **Open Issues:** {{ report.issue_data.open_issues }}
- **Closed Issues:** {{ report.issue_data.closed_issues }}
- **Issue Trends:** {{ report.issue_data.trends }}

### Major Identified Bugs & Problems
{% if report.issue_data.major_bugs %}
{% for bug in report.issue_data.major_bugs %}
- {{ bug }}
{% endfor %}
{% else %}
- No recurring critical bugs detected in sampled issues.
{% endif %}

### Recurring Problems
{% if report.issue_data.recurring_problems %}
{% for problem in report.issue_data.recurring_problems %}
- {{ problem }}
{% endfor %}
{% else %}
- No systemic recurring patterns detected.
{% endif %}

### Feature Requests & Enhancements
{% if report.issue_data.feature_requests %}
{% for feat in report.issue_data.feature_requests %}
- {{ feat }}
{% endfor %}
{% else %}
- No prominent feature request backlog in sampled issues.
{% endif %}

---

## 3. Pull Request Analysis

- **Total PRs Analyzed:** {{ report.pr_data.total_prs_analyzed }}
- **Open PRs:** {{ report.pr_data.open_prs }}
- **Merged PRs:** {{ report.pr_data.merged_prs }}
- **Closed (Unmerged) PRs:** {{ report.pr_data.closed_unmerged_prs }}
- **PR Cadence Trends:** {{ report.pr_data.development_trends }}

### Important Pull Requests
{% if report.pr_data.important_prs %}
{% for pr in report.pr_data.important_prs %}
- {{ pr }}
{% endfor %}
{% else %}
- No large architectural PRs currently pending.
{% endif %}

### Large or Risky Changes
{% if report.pr_data.risky_changes %}
{% for risk in report.pr_data.risky_changes %}
- ⚠️ {{ risk }}
{% endfor %}
{% else %}
- No high-risk PR modifications identified.
{% endif %}

### Frequently Modified Files
{% if report.pr_data.frequently_changed_files %}
{% for file in report.pr_data.frequently_changed_files %}
- `{{ file }}`
{% endfor %}
{% else %}
- Modifications are distributed evenly across modules.
{% endif %}

---

## 4. Branch & Git History Analysis

- **Total Branches:** {{ report.git_data.total_branches }}
- **Active Branches:** {{ report.git_data.active_branches | join(', ') if report.git_data.active_branches else "Default branch only" }}
- **Stale Branches:** {{ report.git_data.stale_branches | join(', ') if report.git_data.stale_branches else "None detected" }}
- **Commit Frequency:** {{ report.git_data.commit_frequency_summary }}
- **Velocity Trends:** {{ report.git_data.velocity_trends }}

### Top Contributors
{% if report.git_data.top_contributors %}
{% for contrib in report.git_data.top_contributors %}
- {{ contrib }}
{% endfor %}
{% else %}
- Contribution data distributed across recent commits.
{% endif %}

---

## 5. Code Architecture & Structure

- **Analyzed Modules:** {{ report.code_data.total_modules_analyzed }}
- **Classes Count:** {{ report.code_data.classes_count }}
- **Functions/Components Count:** {{ report.code_data.functions_count }}
- **Architectural Style:** {{ report.dependency_data.architectural_pattern }}

### Key Source Directories
{% for d in report.code_data.source_directories %}
- `{{ d }}/`
{% endfor %}

---

## 6. Dependency Graph & Workflow

```mermaid
{{ report.dependency_data.mermaid_diagram }}
```

- **Entry Points:** {{ report.dependency_data.entry_point_nodes | join(', ') if report.dependency_data.entry_point_nodes else "None explicit" }}
- **Leaf Components:** {{ report.dependency_data.leaf_nodes | join(', ') if report.dependency_data.leaf_nodes else "None" }}
- **Circular Dependencies:** {{ report.dependency_data.circular_dependencies | join('; ') if report.dependency_data.circular_dependencies else "None detected" }}

---

## 7. Repository Intelligence & Risk Assessment

### Health Evaluation
- **Health Score:** {{ report.intelligence.repository_health_score }} / 100 ({{ report.intelligence.health_status }})
- **Testing Situation:** {{ report.intelligence.testing_situation }}
- **Documentation Quality:** {{ report.intelligence.documentation_quality }}
- **Maintainability:** {{ report.intelligence.maintainability_score }}

### Potential Risks & Vulnerabilities
{% if report.intelligence.potential_risks %}
{% for r in report.intelligence.potential_risks %}
- ⚠️ {{ r }}
{% endfor %}
{% else %}
- No critical architectural or operational risks detected.
{% endif %}

### Technical Debt
{% if report.intelligence.potential_technical_debt %}
{% for td in report.intelligence.potential_technical_debt %}
- 📌 {{ td }}
{% endfor %}
{% else %}
- Minimal technical debt identified in scanned files.
{% endif %}

---

## 8. Actionable Recommendations

### High Priority
{% if report.intelligence.recommendations_high %}
{% for rec in report.intelligence.recommendations_high %}
- **[{{ rec.category }}]** {{ rec.description }}
  - *Rationale:* {{ rec.rationale }}
  {% if rec.suggested_fix %}- *Suggested Fix:* `{{ rec.suggested_fix }}`{% endif %}
{% endfor %}
{% else %}
- None.
{% endif %}

### Medium Priority
{% if report.intelligence.recommendations_medium %}
{% for rec in report.intelligence.recommendations_medium %}
- **[{{ rec.category }}]** {{ rec.description }}
  - *Rationale:* {{ rec.rationale }}
{% endfor %}
{% else %}
- None.
{% endif %}

### Low Priority
{% if report.intelligence.recommendations_low %}
{% for rec in report.intelligence.recommendations_low %}
- **[{{ rec.category }}]** {{ rec.description }}
  - *Rationale:* {{ rec.rationale }}
{% endfor %}
{% else %}
- None.
{% endif %}

---

## 9. How to Run Locally

> **Status:** *{{ report.how_to_run.confidence_label }}*

### Prerequisites
{% for prereq in report.how_to_run.prerequisites %}
- {{ prereq }}
{% endfor %}

### Installation Procedure
```bash
{% for step in report.how_to_run.installation_steps %}
{{ step }}
{% endfor %}
```

### Configuration
```bash
{% for step in report.how_to_run.configuration_steps %}
{{ step }}
{% endfor %}
```

### Execution
```bash
{% for step in report.how_to_run.execution_steps %}
{{ step }}
{% endfor %}
```

---

## 10. Conclusion

{{ report.intelligence.development_activity_summary }}
