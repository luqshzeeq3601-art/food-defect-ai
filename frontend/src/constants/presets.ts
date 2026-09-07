export interface PresetSample {
  id: string;
  name: string;
  path: string;
  category: 'defective' | 'healthy' | 'empty';
  expectedGrade?: 'REJECT' | 'PASS_GRADE_B' | 'PASS_GRADE_A' | 'NO_OBJECT';
  badgeText?: string;
  description: string;
}

export const PRESET_SAMPLES: PresetSample[] = [
  {
    id: 'proof_reject_rot',
    name: 'Active Rot & Decay (REJECT)',
    path: '/samples/proof_01_reject_rot.jpg',
    category: 'defective',
    expectedGrade: 'REJECT',
    badgeText: 'REJECT',
    description: 'Industrial sample with active rot lesion triggering immediate zero-tolerance scrap rejection.',
  },
  {
    id: 'proof_grade_a_healthy',
    name: 'Pristine Produce (GRADE A)',
    path: '/samples/proof_03_grade_a_healthy.jpg',
    category: 'healthy',
    expectedGrade: 'PASS_GRADE_A',
    badgeText: 'GRADE A',
    description: 'Clean surface produce (0.0% defects) meeting strict premium export sorting criteria.',
  },
  {
    id: 'proof_grade_b_blemish',
    name: 'Cosmetic Blemish (GRADE B)',
    path: '/samples/proof_02_grade_b_blemish.jpg',
    category: 'defective',
    expectedGrade: 'PASS_GRADE_B',
    badgeText: 'GRADE B',
    description: 'Minor cosmetic skin blemish (3.0% ratio) routed to commercial processing lane.',
  },
  {
    id: 'proof_empty_conveyor',
    name: 'Empty Conveyor Belt (NO OBJECT)',
    path: '/samples/proof_04_empty_conveyor.jpg',
    category: 'empty',
    expectedGrade: 'NO_OBJECT',
    badgeText: 'NO OBJECT',
    description: 'Empty industrial roller frame demonstrating 0% false positive alarm suppression.',
  },
  {
    id: 'reject_rot_secondary',
    name: 'Severe Rot Lesion (REJECT)',
    path: '/samples/defective_apple_rot.jpg',
    category: 'defective',
    expectedGrade: 'REJECT',
    badgeText: 'REJECT',
    description: 'Severe structural rot infection triggering immediate pneumatic ejector rejection.',
  },
  {
    id: 'grade_a_export',
    name: 'Export Standard Apple (GRADE A)',
    path: '/samples/sample_fruit_grade_a.jpg',
    category: 'healthy',
    expectedGrade: 'PASS_GRADE_A',
    badgeText: 'GRADE A',
    description: 'Zero surface degradation meeting USDA / EU Grade A fresh packaging standards.',
  },
  {
    id: 'grade_b_bruise',
    name: 'Surface Bruise / Scab (GRADE B)',
    path: '/samples/sample_fruit_grade_b.jpg',
    category: 'defective',
    expectedGrade: 'PASS_GRADE_B',
    badgeText: 'GRADE B',
    description: 'Slight mechanical abrasion under 5% surface threshold routed for commercial canning.',
  },
  {
    id: 'conveyor_belt_standby',
    name: 'Clean Roller Belt (NO OBJECT)',
    path: '/samples/conveyor_empty_01.jpg',
    category: 'empty',
    expectedGrade: 'NO_OBJECT',
    badgeText: 'NO OBJECT',
    description: 'Unloaded motorized belt surface validating noise cancellation algorithms.',
  },
];
