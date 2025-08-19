# Serializer changes

## 3.4.4

### v3

* Increment the characters limit of `OrderLineDisplayNativeSerializer.target_url` from 400 to 2000.

## 3.4.2

### v3

* Let `creatives_template` to be mandatory again, but nullable. **Note:** It cannot be null when the `creatives_creator` is not the Customer (`1`).


## 3.4.1

### v3

* Let `creatives_template` from `OrderLineInAppSerializer` to be optional. **Note:** It will remain mandatory when the
`creatives_creator` is not the Customer (`1`).

## 3.2.2

### v3

* Issue a `DeprecationWarning` if a deprecated constant from `easys_ordermanager.v3.serializer` is used.

#### `OrderLineDisplayPremiumSerializer`

* Deprecate `DISPLAY_TARGETING_` constants for `interest_targeting` field, will be removed in v4.
* `interest_targeting` field now accepts arbitrary integer values. Invalid values will be ignored.

## 3.2.1

### v3

#### `OrderLineDisplayPremiumSerializer`

* Deprecate `DISPLAY_AGE_14_29` choice for `age_targeting` field, will be removed in v4.
* Add `DISPLAY_AGE_18_29` choice as a replacement.

## 3.2.0

### v3

#### `OrderLineDisplayNativeSerializer`

* Add `campaign_goal` field, optional.
* Add `target_page_type` field, optional in v3, will be required in v4.

#### `OrderLineDisplayPremiumSerializer`

* Add `customer_wishes` field, optional.

#### `DisplayNativeCreativeSerializer`

* Deprecate `info_for_webdesign` field, will be removed in v4.
* Add `customer_wishes` field, optional, as a replacement.

## 3.1.0

### v3

#### `OrderLineListingSerializer`

* Add `company_name` field, optional. Will default to customer name if not provided.

## 2.10.0

### v3

#### `DisplayNativeCreativeSerializer`

* Removed `NATIVE_AD_FLOW_AD_IN` (`4`) from `ad_type` choices.
* Removed `NATIVE_AD_FLOW_AD_OUT` (`5`) from `ad_type` choices.
* Removed `NATIVE_AD_FLOW_AD_PROSPECT` (`6`) from `ad_type` choices.

## 2.9.0

### v3

#### `OrderLineSeoSerializer`

* Add new field: `location_names`
* Make `regions` field not required anymore
* Increase the maximum length of each item, for `topics` field.

#### `OrderLineGoogleAdsPremiumSerializer`

* Add `EXISTING_STROER_LANDINGPAGE` (`4`) to `target_page_type` choices

## 2.8.0

### v3

#### `DisplayNativeCreativeSerializer`

* Add `NATIVE_VIDEO_AD` (`7`) to `ad_type` choices.

## 2.5.1

### v3

#### `OrderLineInAppSerializer`

* Add `gender_targeting` field, optional.
* Add `age_targeting_from` field, optional.
* Add `age_targeting_to` field, optional.

## 2.5.0

### v1, v2, v3

#### `OrderLineListingSerializer`

* Increased max length of `opening_hours_description` field to 255

### v3

#### `ContactSerializer`
* Removed deprecated `is_primary_contact` field.

#### `AccountSerializer`
* Removed deprecated `campaign_goal` field.
* Removed deprecated `usp` field.
* Removed deprecated `description` field.

## 2.4.0

### v3

#### 
* Added optional `basic_template` to `OrderLineWebsiteSerializer`
  to chose template for basic product level websites from `WEBSITE_BASIC_TEMPLATE_CHOICES`

## 2.3.0

### v3

#### `OrderLineGoogleAdsPremiumSerializer`
* Increased max length of `campaign_goal` field to 1000.

#### `ContactSerializer`
* Added field `opt_in_reviews`, optional.
* Added field `opt_in_listing_reminders`, optional.

## 2.2.5

### v3

#### `AccountLocationSerializer`
* let field `billing_name` to be optional.

## 2.2.4

### v3

#### `AccountLocationSerializer`
* Added field `billing_name`.

## 2.2.3

### v3

#### `OrderLineWebsiteSerializer`
* Added field `internal_area`.

## 2.2.2

### v3

#### `OrderLineEmailSerializer`
* Renamed field `included_accounts` to `included_addresses`.
* Renamed field `additional_accounts` to `additional_addresses`.

## 2.1.3

### v2/v3

#### `OrderLineInAppSerializer`
* Added `INAPP_AUDIENCE_EMPTY` to `target_audiences` choices.

## 2.1.2

#### `OrderLineGoogleAdsPremiumSerializer`
* Made `target_page_type` required.
* Removed fields:
  - `expected_clicks`
  - `expected_conversions`
  - `expected_impression_share`
  - `expected_impressions`
  - `keywords_with_zero_search_volume`
  - `branch_codes`
  - `call_to_action`
  - `is_generic_campaign`
  - `generic_topics`
  - `remarketing_setup_fee`
  - `remarketing_budget`

#### `OrderLineLandingpageSerializer`
* Added field `easys_related_orderline_id`, referencing the easys ID of a product in the same payload, required.

## 2.1.1

### v2/v3

#### `EXISTING_STROER_LANDINGPAGE`

* Change constant value from 3 to 4, to prevent clashes with `NEW_LANDINGPAGE` constant.

#### `validate_website_and_landingpage_exists()`

* `needs_website` is `True` **only** when `target_page_type` property corresponds to a new website. This was the behavior before the version `2.0.10` of the serializer.

## 2.1.0

### v3

#### `PRODUCT_TYPE_CHOICES`

* Added choice `PRODUCT_TYPE_DOMAIN`

#### `OrderLineDomainSerializer`
* Added serializer, the domain fields of `OrderLineWebsiteSerializer`and `OrderLineEmailSerializer` have been migrated to
  this serializer. Contains the following fields:
    * `desired_domain`: character field of maximum length 100, required
    * `domain_type`: choice of `DOMAIN_TYPE_CHOICES`, required
    * `domain_info`: character field of maximum length 100, optional

#### `OrderLineWebsiteSerializer`
* Removed domain fields (`desired_domain`, `domain_type`, `domain_info`)
* Added field `easys_orderline_domain_id`, referencing the easys ID of a domain product in the same payload

#### `OrderLineEmailSerializer`
* Removed domain fields (`desired_domain`, `domain_type`, `domain_info`)
* Added field `easys_orderline_domain_id`, referencing the easys ID of a domain product in the same payload.
* Changed field `included_accounts` to accept a non-empty list of emails, required
* Changed field `additional_accounts` to accept a possibly empty list of additional emails, required
* Removed field `addresses`

#### `OrderLineSerializer`
* Added new field `down_payment`, optional
* Added new field `detail_domain` accepting `OrderLineDomainSerializer` data, optional

#### `Serializer`

* Added validation: if any OrderLine detail contains `easys_orderline_domain_id` it must reference a domain
  product provided in the same payload

## 2.0.12

### v2

#### `OrderLineGoogleAdsPremiumSerializer`

* Remove fields `remarketing_setup_fee` and `remarketing_budget`, since they are no longer used.

## 2.0.11

### v1/v2

#### `OrderLineSeoSerializer`

* Add translation for `EXISTING_STROER_LANDINGPAGE`

## 2.0.10

### v1/v2

#### `OrderLineSeoSerializer`

* Add `campaign_goal` field, not required.
* Support new value (`3`) for `target_page_type` field. It corresponds to `EXISTING_STROER_LANDINGPAGE`.

## 2.0.9

### v2

#### `OrderSerializer`

* Add `salesforce_opportunity_id` field, required.

## 2.0.8

### v1/v2

#### `OrderLineDisplayNativeSerializer`

* Remove required `target_url`.

## 2.0.7

### v2

#### `OrderLineSerializer`

* Add `salesforce_opportunity_line_item_id` field, not required.

## 2.0.6

### v1/v2

#### `OrderLineDisplayNativeSerializer`

* Fix validation when `age_group_from` and `age_group_from` are `null`.

## 2.0.3

### v1/v2

#### `DisplayNativeCreativeSerializer`

* Changed `teaser` and `advertorial` to accept null instead of blank, and removed `allow_blank` from `ad_type`.

## 1.4.53

### v1/v2

#### `OrderLineGoogleAdsPremiumSerializer`

* Add `ticket_id` field, not required.

## 1.4.52

### v1/v2

#### `OrderLineDisplayNativeSerializer`

* Introduced new serializer - `OrderLineDisplayNativeSerializer`

## 1.4.51

### v1/v2

#### `OrderLineInAppSerializer`

* Set `poi_targeting_file` as not required.

## 1.4.50

### v1/v2

#### `OrderLineInAppSerializer`

* Add `poi_targeting_file` field.

## 1.4.49

### v1/v2

#### `OrderLineSerializer`

* Add `is_pre_briefing_necessary` field, default value is False.

## 1.4.48

### v1/v2

#### `OrderLineDisplayPremiumSerializer`

* Add validation for `impressions_per_month` and `impressions_one_time`, depending on `booking_type` (continuous or fixed).

## 1.4.47

### v1/v2

#### `OrderLineDisplayPremiumSerializer`

* Changed field `impressions_per_day` to `impressions_one_time`.

## 1.4.45

### v1/v2

#### `OrderLineDisplayPremiumSerializer`

* Changed field `age_targeting` choices: `DISPLAY_AGE_CHOICES`, removed legacy `[DISPLAY_AGE_14_19, DISPLAY_AGE_20_29]` and added `DISPLAY_AGE_14_29`

## 1.4.44
### v1/v2

* removed `detail_google_ads_basic` from `OrderLineSerializer`
* removed `OrderLineGoogleAdsBasicSerializer`

## 1.4.43
### v2

* removed `detail_display_basic` from `OrderLineSerializer`
* removed `OrderLineDisplayBasicSerializer`


## 1.4.42

### v1

#### `OrderLineGoogleAdsPremiumSerializer`

* Add field `branch_codes`, optional.


## 1.4.39

### v1/v2

#### `OrderLineDisplayPremiumSerializer`

* Add new field `short_name`, optional.

## 1.4.37

### v1/v2

#### `OrderLineEmailSerializer`

* Add necessary and additional fields for domain creation on email orderline: `desired_domain`, `domain_type` and `domain_info`.


## 1.4.36

### v1/v2

#### `OrderLineGoogleAdsPremiumSerializer`

* Add new fields for generic campaign information: `is_generic_campaign` and `generic_topics`, optionals.

## 1.4.34

### v1/v2

#### `OrderLineSeoSerializer`

* Make `ticket_id` optional.

## 1.4.33

### v1/v2

#### `ContactSerializer`

* Add new field `opt_in_marketing`, optional.

## 1.4.32

### v1/v2

#### `OrderLineSeoSerializer`

* Make `regions` optional.

## 1.4.29

### v1/v2

#### `OrderLineInAppSerializer`

* Remove INAPP_AUDIENCE_OTHER choice
* Make `target_audiences` optional. One of the `target_audiences` and `other_target_audiences` is required

## 1.4.25

### v1/v2

#### `OrderLineSerializer`

* Add new field: `payment_cycle`: choice of `PRODUCT_PAYMENT_CYCLE_CHOICES`, optional

## 1.4.24

### v1/v2

#### `OrderLineListingSerializer`

* Add two new fields: `tonline_costs` and `tonline_city`

### `PRODUCT_TYPE_CHOICES`

* Add choice `PRODUCT_TYPE_TONLINE`

## 1.4.23

### v1/v2

#### `AccountLocationSerializer`

* Add validation: required `payment_debit_account_iban` in case of `payment_type` Charge

## 1.4.12

### v2

#### `OrderLineWebsiteSerializer`

* Added proper choices for
    * `design_preference_minimalistic_embellished`
    * `design_preference_modern_classic`
    * `design_preference_simple_striking`
    * `design_preference_text_picture`

## 1.4.10

### v1/v2

#### `OrderLineFacebookSerializer`
* `ages` choices adjustment: `14_18` is now `13_17` and `19_24` is `18_24`

## 1.4.9

### v2

#### `OrderLineWebsiteSerializer`
* Restrict validator for field `desired_domain` to accept only domain names without http protocol and no IP addresses

## 1.4.6

### v1 / v2

#### `OrderLineGoogleAdsPremiumSerializer`
* Add optional `expected_impressions` and `expected_impression_share`

### v1

* Add optional `target_page_type`

## 1.4.5

### v1 / v2

#### `AccountLocationSerializer`
* Allow `google_places_id` to be 1000 characters max (was 30 before)

## 1.4.3

### v2

#### `OrderLineWebsiteSerializer`
* `additional_subpages` must be >= 0 and <= 60 now

#### `OrderLineGoogleAdsBasicSerializer`
* added optional `target_url`

#### `OrderLineGoogleAdsPremiumSerializer`
* added optional `target_url`

## 1.4.2

### v2

#### `AccountSerializer`
* `branch_codes` cannot be empty any more

#### `OrderLineSeoSerializer`
* `topics` cannot be empty any more
* `regions` cannot be empty any more

#### `OrderLineGoogleAdsBasicSerializer`
* `regions` cannot be empty any more

## 1.4.1

### v2

#### `OrderLineLandingpageSerializer`
added, similar to `OrderLineWebsiteSerializer` except for
* `additional_subpages`: positive integer, required
* `logo_creation`: choice of `LOGO_CREATION_CHOICES`, required

#### `OrderLineSerializer`
* added `detail_landingpage`: type `OrderLineLandingpageSerializer`, only required when OrderLine represents a landingpage product

#### `OrderLineGoogleAdsBasicSerializer`
* added `target_page_type`: choice of `GOOGLE_ADS_LANDING_PAGE_CHOICES`, optional
    * see `Serializer` changes for validation

#### `OrderLineGoogleAdsPremiumSerializer`
* added `branch_codes`: list of HeroCentral provided industry topic codes, optional
    * HeroCentral will validate the codes against the industry tree
* added `target_page_type`: choice of `GOOGLE_ADS_LANDING_PAGE_CHOICES`, optional
    * see `Serializer` changes for validation
* added `remarketing_setup_fee`: decimal, must be >=0 if `include_remarketing=true`
* added `remarketing_budget`: decimal, must be >=0 if `include_remarketing=true`

#### Validations
* added validation: if any OrderLine detail contains `target_page_type`
    * if set to `NEW_WEBSITE`, the serializer will require an OrderLine of type `PRODUCT_TYPE_WEBSITE` to exist
    * if set to `NEW_LANDINGPAGE`, the serializer will require an OrderLine of type `PRODUCT_TYPE_LANDINGPAGE` to exist
    * OrderLine details which can provide values for `target_page_type` are:
        * OrderLineDisplayBasicSerializer
        * OrderLineDisplayPremiumSerializer
        * OrderLineSeoSerializer
        * OrderLineInAppSerializer
        * OrderLineFacebookSerializer
