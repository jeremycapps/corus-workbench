profile: customer-value-architect
version: 1.0.0

purpose: >
  Help a Customer Value Architect translate a model output into customer-specific
  workforce, labor, and money value.

audience:
  role: Customer Value Architect
  organization: Neara
  customer: Southern California Edison

primary_question: >
  How do I turn this model output into customer adoption, value validation,
  and measurable operating impact?

information_hierarchy:
  hero:
    - prop: value_outputs.total_validation_exposure
      component: kpi_card
      priority: 1

    - prop: value_outputs.total_person_hours
      component: kpi_card
      priority: 2

    - prop: value_outputs.crew_days_required
      component: kpi_card
      priority: 3

    - prop: context_input.added_watch_items
      component: kpi_card
      priority: 4

  relational:
    - prop: source_context.domain
      component: breadcrumbs

    - prop: source_context.surface
      component: breadcrumbs

  collection:
    - prop: customer_constraints
      component: data_table

    - prop: value_calculations
      component: data_table

  granular:
    - prop: context_input.because
      component: description_list

actions:
  primary:
    - generate_value_summary
    - export_customer_packet
    - compare_assumptions
    - update_value_constraints
