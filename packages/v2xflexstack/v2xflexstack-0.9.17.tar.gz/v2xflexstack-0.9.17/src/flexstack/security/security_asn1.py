# pylint: skip-file
SECURITY_ASN1_DESCRIPTIONS = """--***************************************************************************--
--                     IEEE Std 1609.2: Base Data Types                      --
--***************************************************************************--

/** 
 * @brief NOTE: Section references in this file are to clauses in IEEE Std
 * 1609.2 unless indicated otherwise. Full forms of acronyms and
 * abbreviations used in this file are specified in 3.2. 
 */

Ieee1609Dot2BaseTypes {iso(1) identified-organization(3) ieee(111) 
  standards-association-numbered-series-standards(2) wave-stds(1609) dot2(2)
  base(1) base-types(2) major-version-2(2) minor-version-3(3)}

DEFINITIONS AUTOMATIC TAGS ::= BEGIN 
 
EXPORTS ALL;

--***************************************************************************--
--                               Integer Types                               --
--***************************************************************************--

/** 
 * @class Uint3
 *
 * @brief This atomic type is used in the definition of other data structures.
 * It is for non-negative integers up to 7, i.e., (hex)07.
 */
  Uint3  ::= INTEGER (0..7)

/** 
 * @class Uint8
 *
 * @brief This atomic type is used in the definition of other data structures.
 * It is for non-negative integers up to 255, i.e., (hex)ff.
 */
  Uint8  ::= INTEGER (0..255)
  
/** 
 * @class Uint16
 *
 * @brief This atomic type is used in the definition of other data structures.
 * It is for non-negative integers up to 65,535, i.e., (hex)ff ff.
 */
  Uint16 ::= INTEGER (0..65535)
  
/** 
 * @class Uint32
 *
 * @brief This atomic type is used in the definition of other data structures.
 * It is for non-negative integers up to 4,294,967,295, i.e.,
 * (hex)ff ff ff ff.
 */
  Uint32 ::= INTEGER (0..4294967295)
  
/** 
 * @class Uint64
 *
 * @brief This atomic type is used in the definition of other data structures.
 * It is for non-negative integers up to 18,446,744,073,709,551,615, i.e.,
 * (hex)ff ff ff ff ff ff ff ff.
 */
  Uint64 ::= INTEGER (0..18446744073709551615)
  
/** 
 * @class SequenceOfUint8
 *
 * @brief This type is used for clarity of definitions.
 */
  SequenceOfUint8  ::= SEQUENCE OF Uint8

/** 
 * @class SequenceOfUint16
 *
 * @brief This type is used for clarity of definitions.
 */
  SequenceOfUint16 ::= SEQUENCE OF Uint16


--***************************************************************************--
--                            OCTET STRING Types                             --
--***************************************************************************--

/** 
 * @class Opaque
 *
 * @brief This is a synonym for ASN.1 OCTET STRING, and is used in the
 * definition of other data structures.
 */
  Opaque ::= OCTET STRING
  
/** 
 * @class HashedId3
 *
 * @brief This type contains the truncated hash of another data structure.
 * The HashedId3 for a given data structure is calculated by calculating the
 * hash of the encoded data structure and taking the low-order three bytes of
 * the hash output. If the data structure is subject to canonicalization it
 * is canonicalized before hashing. The low-order three bytes are the last
 * three bytes of the hash when represented in network byte order. See
 * Example below.
 *
 * <br><br><b>Example</b>: Consider the SHA-256 hash of the empty string:
 *
 * <br>SHA-256("") =
 * e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b78<b>52b855</b>
 *
 * <br><br>The HashedId3 derived from this hash corresponds to the following:
 * 
 * <br>HashedId3 = 52b855.
 */
  HashedId3 ::= OCTET STRING (SIZE(3))

/** 
 * @class SequenceOfHashedId3
 *
 * @brief This type is used for clarity of definitions.
 */
  SequenceOfHashedId3 ::= SEQUENCE OF HashedId3

/** 
 * @class HashedId8
 *
 * @brief This type contains the truncated hash of another data structure.
 * The HashedId8 for a given data structure is calculated by calculating the
 * hash of the encoded data structure and taking the low-order eight bytes of
 * the hash output. If the data structure is subject to canonicalization it
 * is canonicalized before hashing. The low-order eight bytes are the last
 * eight bytes of the hash when represented in network byte order. See
 * Example below.
 *
 * <br><br>The hash algorithm to be used to calculate a HashedId8 within a
 * structure depends on the context. In this standard, for each structure
 * that includes a HashedId8 field, the corresponding text indicates how the
 * hash algorithm is determined.
 *
 * <br><br><b>Example</b>: Consider the SHA-256 hash of the empty string:
 *
 * <br>SHA-256("") =
 * e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934c<b>a495991b7852b855</b>
 *
 * <br><br>The HashedId8 derived from this hash corresponds to the following:
 *
 * <br>HashedId8 = a495991b7852b855.
 */
  HashedId8 ::= OCTET STRING (SIZE(8))
  
/** 
 * @class HashedId10
 *
 * @brief This type contains the truncated hash of another data structure.
 * The HashedId10 for a given data structure is calculated by calculating the
 * hash of the encoded data structure and taking the low-order ten bytes of
 * the hash output. If the data structure is subject to canonicalization it
 * is canonicalized before hashing. The low-order ten bytes are the last ten
 * bytes of the hash when represented in network byte order. See Example below.
 *
 * <br><br>The hash algorithm to be used to calculate a HashedId10 within a
 * structure depends on the context. In this standard, for each structure
 * that includes a HashedId10 field, the corresponding text indicates how the
 * hash algorithm is determined.
 *
 * <br><br><b>Example</b>: Consider the SHA-256 hash of the empty string:
 *
 * <br>SHA-256("") =
 * e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b<b>934ca495991b7852b855</b>
 *
 * <br><br>The HashedId10 derived from this hash corresponds to the following:
 *
 * <br>HashedId10 = 934ca495991b7852b855.
 */
  HashedId10 ::= OCTET STRING (SIZE(10))
  
/** 
 * @class HashedId32
 *
 * @brief This type contains the truncated hash of another data structure.
 * The HashedId32 for a given data structure is calculated by calculating the
 * hash of the encoded data structure and taking the low-order thirty two 
 * bytes of the hash output. If the data structure is subject to
 * canonicalization it is canonicalized before hashing. The low-order thirty
 * two bytes are the last thirty two bytes of the hash when represented in
 * network byte order. See Example below.
 *
 * <br><br>The hash algorithm to be used to calculate a HashedId32 within a
 * structure depends on the context. In this standard, for each structure
 * that includes a HashedId32 field, the corresponding text indicates how the
 * hash algorithm is determined.
 *
 * <br><br><b>Example</b>: Consider the SHA-256 hash of the empty string:
 *
 * <br>SHA-256("") =
 * e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
 *
 * <br><br>The HashedId32 derived from this hash corresponds to the following:
 * 
 * <br>HashedId32 =
 * e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.
 */
  HashedId32 ::= OCTET STRING (SIZE(32))
 
--***************************************************************************--
--                             Time Structures                               --
--***************************************************************************--

/** 
 * @class Time32
 *
 * @brief This type gives the number of (TAI) seconds since 00:00:00 UTC, 1
 * January, 2004.
 */
  Time32 ::= Uint32

/** 
 * @class Time64
 *
 * @brief This type gives the number of (TAI) microseconds since 00:00:00
 * UTC, 1 January, 2004.
 */
  Time64 ::= Uint64

/** 
 * @class ValidityPeriod
 *
 * @brief This structure gives the validity period of a certificate. The
 * start of the validity period is given by start and the end is given by
 * start + duration.
 *
 * @param start contains the starting time of the validity period.
 *
 * @param duration contains the duration of the validity period.
 */
  ValidityPeriod ::= SEQUENCE {
    start     Time32,
    duration  Duration
  }

/** 
 * @class Duration
 *
 * @brief This structure represents the duration of validity of a
 * certificate. The Uint16 value is the duration, given in the units denoted
 * by the indicated choice. A year is considered to be 31556952 seconds,
 * which is the average number of seconds in a year; if it is desired to map
 * years more closely to wall-clock days, this can be done using the hours
 * choice for up to seven years and the sixtyHours choice for up to 448. In
 * this structure: 
 *
 * @param microseconds contains the duration in microseconds.
 *
 * @param milliseconds contains the duration in milliseconds.
 *
 * @param seconds contains the duration in seconds.
 *
 * @param minutes contains the duration in minutes.
 *
 * @param hours contains the duration in hours.
 *
 * @param sixtyHours contains the duration in sixty-hour periods.
 *
 * @param years contains the duration in years.
 */
  Duration ::= CHOICE {
    microseconds  Uint16,
    milliseconds  Uint16,
    seconds       Uint16,
    minutes       Uint16,
    hours         Uint16,
    sixtyHours    Uint16,
    years         Uint16
  } 


--***************************************************************************--
--                           Location Structures                             --
--***************************************************************************--

/** 
 * @class GeographicRegion
 *
 * @brief This structure represents a geographic region of a specified form.
 * A certificate is not valid if any part of the region indicated in its
 * scope field lies outside the region indicated in the scope of its issuer.
 *
 * <br><br><b>Critical information fields</b>:
 * <ul>
 * <li> If present, this is a critical information field as defined in 5.2.6.
 * An implementation that does not recognize the indicated CHOICE when
 * verifying a signed SPDU shall indicate that the signed SPDU is invalid.</li>
 *
 * <li> If selected, rectangularRegion is a critical information field as
 * defined in 5.2.6. An implementation that does not support the number of
 * RectangularRegion in rectangularRegions when verifying a signed SPDU shall
 * indicate that the signed SPDU is invalid. A compliant implementation shall
 * support rectangularRegions fields containing at least eight entries.</li>
 *
 * <li> If selected, identifiedRegion is a critical information field as
 * defined in 5.2.6. An implementation that does not support the number of
 * IdentifiedRegion in identifiedRegion shall reject the signed SPDU as
 * invalid. A compliant implementation shall support identifiedRegion fields
 * containing at least eight entries.</li>
 * </ul>
 *
 * <b>Parameters</b>:
 *
 * @param circularRegion contains a single instance of the CircularRegion
 * structure.
 *
 * @param rectangularRegion is an array of RectangularRegion structures
 * containing at least one entry. This field is interpreted as a series of
 * rectangles, which may overlap or be disjoint. The permitted region is any
 * point within any of the rectangles. 
 *
 * @param polygonalRegion contains a single instance of the PolygonalRegion
 * structure.
 *
 * @param identifiedRegion is an array of IdentifiedRegion structures
 * containing at least one entry. The permitted region is any point within
 * any of the identified regions.
 */
  GeographicRegion ::= CHOICE {
    circularRegion     CircularRegion,
    rectangularRegion  SequenceOfRectangularRegion,
    polygonalRegion    PolygonalRegion,
    identifiedRegion   SequenceOfIdentifiedRegion,
    ...
  }

/** 
 * @class CircularRegion
 *
 * @brief This structure specifies a circle with its center at center, its
 * radius given in meters, and located tangential to the reference ellipsoid.
 * The indicated region is all the points on the surface of the reference
 * ellipsoid whose distance to the center point over the reference ellipsoid
 * is less than or equal to the radius. A point which contains an elevation
 * component is considered to be within the circular region if its horizontal
 * projection onto the reference ellipsoid lies within the region.
 */
  CircularRegion ::= SEQUENCE {
    center  TwoDLocation,
    radius  Uint16
  }

/** 
 * @class RectangularRegion
 *
 * @brief This structure specifies a rectangle formed by connecting in
 * sequence: (northWest.latitude, northWest.longitude), (southEast.latitude,
 * northWest.longitude), (southEast.latitude, southEast.longitude), and
 * (northWest.latitude, southEast.longitude). The points are connected by
 * lines of constant latitude or longitude. A point which contains an
 * elevation component is considered to be within the rectangular region if
 * its horizontal projection onto the reference ellipsoid lies within the
 * region. A RectangularRegion is valid only if the northWest value is north
 * and west of the southEast value, i.e., the two points cannot have equal
 * latitude or equal longitude.
 */
  RectangularRegion ::= SEQUENCE {
    northWest  TwoDLocation,
    southEast  TwoDLocation
  }

/** 
 * @class SequenceOfRectangularRegion
 *
 * @brief This type is used for clarity of definitions.
 */
  SequenceOfRectangularRegion ::= SEQUENCE OF RectangularRegion

/** 
 * @class PolygonalRegion
 *
 * @brief This structure defines a region using a series of distinct
 * geographic points, defined on the surface of the reference ellipsoid. The
 * region is specified by connecting the points in the order they appear,
 * with each pair of points connected by the geodesic on the reference
 * ellipsoid. The polygon is completed by connecting the final point to the
 * first point. The allowed region is the interior of the polygon and its
 * boundary. 
 *
 * <br><br>A point which contains an elevation component is considered to be
 * within the polygonal region if its horizontal projection onto the
 * reference ellipsoid lies within the region.
 *
 * <br><br>A valid PolygonalRegion contains at least three points. In a valid
 * PolygonalRegion, the implied lines that make up the sides of the polygon
 * do not intersect. 
 *
 * <br><br><b>Critical information fields</b>:
 * <ul>
 * <li> If present, this is a critical information field as defined in 5.2.6.
 * An implementation that does not support the number of TwoDLocation in the
 * PolygonalRegion when verifying a signed SPDU shall indicate that the signed
 * SPDU is invalid. A compliant implementation shall support PolygonalRegions
 * containing at least eight TwoDLocation entries.</li>
 * </ul>
 */
  PolygonalRegion ::= SEQUENCE SIZE (3..MAX) OF TwoDLocation

/** 
 * @class TwoDLocation
 *
 * @brief This structure is used to define validity regions for use in
 * certificates. The latitude and longitude fields contain the latitude and
 * longitude as defined above. 
 *
 * <br><br>NOTE: This data structure is consistent with the location encoding
 * used in SAE J2735, except that values 900 000 001 for latitude (used to
 * indicate that the latitude was not available) and 1 800 000 001 for
 * longitude (used to indicate that the longitude was not available) are not
 * valid.
 */
  TwoDLocation ::= SEQUENCE {
    latitude   Latitude,
    longitude  Longitude
  }

/** 
 * @class IdentifiedRegion
 *
 * @brief This structure indicates the region of validity of a certificate
 * using region identifiers.
 *
 * <br><br><b>Critical information fields</b>:
 * <ul>
 * <li> If present, this is a critical information field as defined in 5.2.6.
 * An implementation that does not recognize the indicated CHOICE when
 * verifying a signed SPDU shall indicate that the signed SPDU is invalid.</li>
 * </ul>
 */
  IdentifiedRegion ::= CHOICE {
    countryOnly           CountryOnly,
    countryAndRegions     CountryAndRegions,
    countryAndSubregions  CountryAndSubregions,
    ...
  }

/** 
 * @class SequenceOfIdentifiedRegion
 *
 * @brief This type is used for clarity of definitions.
 */
  SequenceOfIdentifiedRegion ::= SEQUENCE OF IdentifiedRegion

/** 
 * @class CountryOnly
 *
 * @brief This is the integer representation of the country or area
 * identifier as defined by the United Nations Statistics Division in October
 * 2013 (see normative references in Clause 2).
 */
  CountryOnly ::= Uint16

/** 
 * @class CountryAndRegions
 *
 * @brief In this structure:
 * 
 * @param countryOnly is a CountryOnly as defined above.
 *
 * @param region identifies one or more regions within the country. If
 * countryOnly indicates the United States of America, the values in this
 * field identify the state or statistically equivalent entity using the
 * integer version of the 2010 FIPS codes as provided by the U.S. Census
 * Bureau (see normative references in Clause 2). For other values of
 * countryOnly, the meaning of region is not defined in this version of this
 * standard.
 */
  CountryAndRegions ::= SEQUENCE {
    countryOnly  CountryOnly,
    regions      SequenceOfUint8
  }

/** 
 * @class CountryAndSubregions
 *
 * @brief In this structure:
 * <br><br><b>Critical information fields</b>:
 * <ul>
 * <li> If present, this is a critical information field as defined in 5.2.6.
 * An implementation that does not recognize RegionAndSubregions or
 * CountryAndSubregions values when verifying a signed SPDU shall indicate
 * that the signed SPDU is invalid. A compliant implementation shall support
 * CountryAndSubregions containing at least eight RegionAndSubregions
 * entries.</li>
 * </ul>
 *
 * <b>Parameters</b>:
 * 
 * @param country is a CountryOnly as defined above.
 *
 * @param regionAndSubregions identifies one or more subregions within
 * country. If country indicates the United States of America, the values in
 * this field identify the county or county equivalent entity using the
 * integer version of the 2010 FIPS codes as provided by the U.S. Census
 * Bureau (see normative references in Clause 2). For other values of
 * country, the meaning of regionAndSubregions is not defined in this version
 * of this standard.
 */
  CountryAndSubregions ::= SEQUENCE {
    country              CountryOnly,
    regionAndSubregions  SequenceOfRegionAndSubregions
  }

/** 
 * @class RegionAndSubregions
 *
 * @brief In this structure:
 * <br><br><b>Critical information fields</b>:
 * <ul>
 * <li> RegionAndSubregions is a critical information field as defined in
 * 5.2.5. An implementation that does not detect or recognize the the region
 * or subregions values when verifying a signed SPDU shall indicate that the
 * signed SPDU is invalid.</li>
 * </ul>
 *  
 * <b>Parameters</b>:
 *
 * @param region identifies a region within a country as specified under
 * CountryAndRegions.
 *
 * @param subregions identifies one or more subregions as specified under
 * CountryAndSubregions.
 */
  RegionAndSubregions ::= SEQUENCE {
    region      Uint8,
    subregions  SequenceOfUint16
  }

/** 
 * @class SequenceOfRegionAndSubregions
 *
 * @brief This type is used for clarity of definitions.
 */
  SequenceOfRegionAndSubregions ::= SEQUENCE OF RegionAndSubregions

/** 
 * @class ThreeDLocation
 *
 * @brief This structure contains an estimate of 3D location. The details of
 * the structure are given in the definitions of the individual fields below.
 *
 * <br><br>NOTE: The units used in this data structure are consistent with the
 * location data structures used in SAE J2735, though the encoding is
 * incompatible.
 */
  ThreeDLocation ::= SEQUENCE {
    latitude   Latitude,
    longitude  Longitude,
    elevation  Elevation
  }

/** 
 * @class Latitude
 *
 * @brief This type contains an INTEGER encoding an estimate of the latitude
 * with precision 1/10th microdegree relative to the World Geodetic System
 * (WGS)-84 datum as defined in NIMA Technical Report TR8350.2.
 */
  Latitude ::= NinetyDegreeInt
  
/** 
 * @class Longitude
 *
 * @brief This type contains an INTEGER encoding an estimate of the longitude
 * with precision 1/10th microdegree relative to the World Geodetic System
 * (WGS)-84 datum as defined in NIMA Technical Report TR8350.2.
 */
  Longitude ::= OneEightyDegreeInt
  
/** 
 * @class Elevation
 *
 * @brief This structure contains an estimate of the geodetic altitude above
 * or below the WGS84 ellipsoid. The 16-bit value is interpreted as an
 * integer number of decimeters representing the height above a minimum
 * height of −409.5 m, with the maximum height being 6143.9 m. 
 */
  Elevation ::= Uint16

/** 
 * @class NinetyDegreeInt
 *
 * @brief The integer in the latitude field is no more than 900,000,000 and
 * no less than −900,000,000, except that the value 900,000,001 is used to
 * indicate the latitude was not available to the sender.
 */
  NinetyDegreeInt ::= INTEGER {
    min 		(-900000000),
    max 		(900000000),
    unknown 	(900000001)
  } (-900000000..900000001)

/** 
 * @class KnownLatitude
 *
 * @brief The known latitudes are from -900,000,000 to +900,000,000 in 0.1
 * microdegree intervals.
 */
  KnownLatitude ::= NinetyDegreeInt (min..max) 

/** 
 * @class UnknownLatitude
 *
 * @brief The value 900,000,001 indicates that the latitude was not
 * available to the sender.
 */
  UnknownLatitude ::= NinetyDegreeInt (unknown)
  
/** 
 * @class OneEightyDegreeInt
 *
 * @brief The integer in the longitude field is no more than 1,800,000,000
 * and no less than −1,799,999,999, except that the value 1,800,000,001 is
 * used to indicate that the longitude was not available to the sender.
 */
  OneEightyDegreeInt ::= INTEGER {
    min      	(-1799999999),
    max      	(1800000000),
    unknown  	(1800000001)
  } (-1799999999..1800000001)

/** 
 * @class KnownLongitude
 *
 * @brief The known longitudes are from -1,799,999,999 to +1,800,000,000 in
 * 0.1 microdegree intervals.
 */
  KnownLongitude ::= OneEightyDegreeInt (min..max)
  
/** 
 * @class UnknownLongitude
 *
 * @brief The value 1,800,000,001 indicates that the longitude was not
 * available to the sender.
 */
  UnknownLongitude ::= OneEightyDegreeInt (unknown)


--***************************************************************************--
--                            Crypto Structures                              --
--***************************************************************************--

/** 
 * @class Signature
 *
 * @brief This structure represents a signature for a supported public key
 * algorithm. It may be contained within SignedData or Certificate.
 *
 * <br><br><b>Critical information fields</b>: If present, this is a critical
 * information field as defined in 5.2.5. An implementation that does not
 * recognize the indicated CHOICE for this type when verifying a signed SPDU
 * shall indicate that the signed SPDU is invalid.
 */
  Signature ::= CHOICE {
    ecdsaNistP256Signature         EcdsaP256Signature,
    ecdsaBrainpoolP256r1Signature  EcdsaP256Signature,
    ...,
    ecdsaBrainpoolP384r1Signature  EcdsaP384Signature,
    ecdsaNistP384Signature         EcdsaP384Signature
  }

/** 
 * @class EcdsaP256Signature
 *
 * @brief This structure represents an ECDSA signature. The signature is
 * generated as specified in 5.3.1.
 *
 * <br><br>If the signature process followed the specification of FIPS 186-4
 * and output the integer r, r is represented as an EccP256CurvePoint
 * indicating the selection x-only.
 *
 * <br><br>If the signature process followed the specification of SEC 1 and
 * output the elliptic curve point R to allow for fast verification, R is
 * represented as an EccP256CurvePoint indicating the choice compressed-y-0,
 * compressed-y-1, or uncompressed at the sender’s discretion.
 *
 * <br><br>Encoding considerations: If this structure is encoded for hashing,
 * the EccP256CurvePoint in rSig shall be taken to be of form x-only.
 *
 * <br><br>NOTE: When the signature is of form x-only, the x-value in rSig is
 * an integer mod n, the order of the group; when the signature is of form
 * compressed-y-*, the x-value in rSig is an integer mod p, the underlying
 * prime defining the finite field. In principle this means that to convert a
 * signature from form compressed-y-* to form x-only, the x-value should be
 * checked to see if it lies between n and p and reduced mod n if so. In
 * practice this check is unnecessary: Haase’s Theorem states that difference
 * between n and p is always less than 2*square-root(p), and so the chance
 * that an integer lies between n and p, for a 256-bit curve, is bounded
 * above by approximately square-root(p)/p or 2^(−128). For the 256-bit
 * curves in this standard, the exact values of n and p in hexadecimal are:
 *
 * <br><br>NISTp256:
 * <ul>
 * <li> p = FFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
 * </li>
 * <li> n = FFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
 * </li>
 * </ul>
 *
 * Brainpoolp256:
 * <ul>
 * <li> p = A9FB57DBA1EEA9BC3E660A909D838D726E3BF623D52620282013481D1F6E5377
 * </li>
 * <li> n = A9FB57DBA1EEA9BC3E660A909D838D718C397AA3B561A6F7901E0E82974856A7
 * </li>
 * </ul>
 */
  EcdsaP256Signature ::= SEQUENCE {
    rSig  EccP256CurvePoint,
    sSig  OCTET STRING (SIZE (32))
  }

/** 
 * @class EcdsaP384Signature
 *
 * @brief This structure represents an ECDSA signature. The signature is
 * generated as specified in 5.3.1.
 *
 * <br><br>If the signature process followed the specification of FIPS 186-4
 * and output the integer r, r is represented as an EccP384CurvePoint
 * indicating the selection x-only.
 *
 * <br><br>If the signature process followed the specification of SEC 1 and
 * output the elliptic curve point R to allow for fast verification, R is
 * represented as an EccP384CurvePoint indicating the choice compressed-y-0,
 * compressed-y-1, or uncompressed at the sender’s discretion. 
 *
 * <br><br>Encoding considerations: If this structure is encoded for hashing,
 * the EccP256CurvePoint in rSig shall be taken to be of form x-only.
 *
 * <br><br>NOTE: When the signature is of form x-only, the x-value in rSig is
 * an integer mod n, the order of the group; when the signature is of form
 * compressed-y-*, the x-value in rSig is an integer mod p, the underlying
 * prime defining the finite field. In principle this means that to convert a
 * signature from form compressed-y-* to form x-only, the x-value should be
 * checked to see if it lies between n and p and reduced mod n if so. In
 * practice this check is unnecessary: Haase’s Theorem states that difference
 * between n and p is always less than 2*square-root(p), and so the chance
 * that an integer lies between n and p, for a 384-bit curve, is bounded
 * above by approximately square-root(p)/p or 2^(−192). For the 384-bit curve
 * in this standard, the exact values of n and p in hexadecimal are:
 * <ul>
 * <li> p = 8CB91E82A3386D280F5D6F7E50E641DF152F7109ED5456B412B1DA197FB71123
 * ACD3A729901D1A71874700133107EC53</li>
 *
 * <li> n = 8CB91E82A3386D280F5D6F7E50E641DF152F7109ED5456B31F166E6CAC0425A7
 * CF3AB6AF6B7FC3103B883202E9046565</li>
 * </ul>
 */
  EcdsaP384Signature ::= SEQUENCE {
    rSig  EccP384CurvePoint,
    sSig  OCTET STRING (SIZE (48))
  }

/** 
 * @class EccP256CurvePoint
 *
 * @brief This structure specifies a point on an elliptic curve in
 * Weierstrass form defined over a 256-bit prime number. This encompasses
 * both NIST p256 as defined in FIPS 186-4 and Brainpool p256r1 as defined in
 * RFC 5639. The fields in this structure are OCTET STRINGS produced with the
 * elliptic curve point encoding and decoding methods defined in subclause
 * 5.5.6 of IEEE Std 1363-2000. The x-coordinate is encoded as an unsigned
 * integer of length 32 octets in network byte order for all values of the
 * CHOICE; the encoding of the y-coordinate y depends on whether the point is
 * x-only, compressed, or uncompressed. If the point is x-only, y is omitted.
 * If the point is compressed, the value of type depends on the least
 * significant bit of y: if the least significant bit of y is 0, type takes
 * the value compressed-y-0, and if the least significant bit of y is 1, type
 * takes the value compressed-y-1. If the point is uncompressed, y is encoded
 * explicitly as an unsigned integer of length 32 octets in network byte order.
 */
  EccP256CurvePoint ::= CHOICE {
    x-only           OCTET STRING (SIZE (32)),
    fill             NULL,
    compressed-y-0   OCTET STRING (SIZE (32)),
    compressed-y-1   OCTET STRING (SIZE (32)),
    uncompressedP256 SEQUENCE  {
      x OCTET STRING (SIZE (32)),
      y OCTET STRING (SIZE (32))
    }
  }

/** 
 * @class EccP384CurvePoint
 *
 * @brief This structure specifies a point on an elliptic curve in
 * Weierstrass form defined over a 384-bit prime number. The only supported
 * such curve in this standard is Brainpool p384r1 as defined in RFC 5639.
 * The fields in this structure are OCTET STRINGS produced with the elliptic
 * curve point encoding and decoding methods defined in subclause 5.5.6 of
 * IEEE Std 1363-2000. The x-coordinate is encoded as an unsigned integer of
 * length 48 octets in network byte order for all values of the CHOICE; the
 * encoding of the y-coordinate y depends on whether the point is x-only,
 * compressed, or uncompressed. If the point is x-only, y is omitted. If the
 * point is compressed, the value of type depends on the least significant
 * bit of y: if the least significant bit of y is 0, type takes the value
 * compressed-y-0, and if the least significant bit of y is 1, type takes the
 * value compressed-y-1. If the point is uncompressed, y is encoded
 * explicitly as an unsigned integer of length 48 octets in network byte order.
 */
  EccP384CurvePoint ::= CHOICE  {
    x-only          OCTET STRING (SIZE (48)),
    fill            NULL,
    compressed-y-0  OCTET STRING (SIZE (48)),
    compressed-y-1  OCTET STRING (SIZE (48)),
    uncompressedP384 SEQUENCE {
      x OCTET STRING (SIZE (48)),
      y OCTET STRING (SIZE (48))
    }
  }

/** 
 * @class SymmAlgorithm
 *
 * @brief This enumerated value indicates supported symmetric algorithms. The
 * only symmetric algorithm supported in this version of this standard is
 * AES-CCM as specified in 5.3.7.
 */
  SymmAlgorithm ::= ENUMERATED { 
    aes128Ccm,
    ...
  }

/** 
 * @class HashAlgorithm
 *
 * @brief This structure identifies a hash algorithm. The value is sha256,
 * indicates SHA-256 as specified in 5.3.3. The value sha384 indicates
 * SHA-384 as specified in 5.3.3.
 *
 * <br><br><b>Critical information fields</b>: This is a critical information
 * field as defined in 5.2.6. An implementation that does not recognize the
 * enumerated value of this type in a signed SPDU when verifying a signed
 * SPDU shall indicate that the signed SPDU is invalid.
 */
  HashAlgorithm ::= ENUMERATED { 
    sha256,
    ...,
    sha384
  }

/** 
 * @class EciesP256EncryptedKey
 *
 * @brief This data structure is used to transfer a 16-byte symmetric key
 * encrypted using ECIES as specified in IEEE Std 1363a-2004. 
 *
 * <br><br>Encryption and decryption are carried out as specified in 5.3.4. 
 *
 * <br><br><b>Parameters</b>: 
 *
 * @param v is the sender’s ephemeral public key, which is the output V from
 * encryption as specified in 5.3.4. 
 *
 * @param c is the encrypted symmetric key, which is the output C from
 * encryption as specified in 5.3.4. The algorithm for the symmetric key is
 * identified by the CHOICE indicated in the following SymmetricCiphertext.
 *
 * @param t is the authentication tag, which is the output tag from
 * encryption as specified in 5.3.4.
 */
  EciesP256EncryptedKey ::= SEQUENCE {
    v  EccP256CurvePoint,
    c  OCTET STRING (SIZE (16)),
    t  OCTET STRING (SIZE (16))
  }

/** 
 * @class EncryptionKey
 *
 * @brief This structure contains an encryption key, which may be a public or
 * a symmetric key.
 */
  EncryptionKey ::= CHOICE {
    public     PublicEncryptionKey,
    symmetric  SymmetricEncryptionKey 
  }

/** 
 * @class PublicEncryptionKey
 *
 * @brief This structure specifies a public encryption key and the associated
 * symmetric algorithm which is used for bulk data encryption when encrypting
 * for that public key.
 */
  PublicEncryptionKey ::= SEQUENCE { 
    supportedSymmAlg  SymmAlgorithm,
    publicKey         BasePublicEncryptionKey
  }

/** 
 * @class BasePublicEncryptionKey
 *
 * @brief This structure specifies the bytes of a public encryption key for a
 * particular algorithm. The only algorithm supported is ECIES over either
 * the NIST P256 or the Brainpool P256r1 curve as specified in 5.3.4.
 */
  BasePublicEncryptionKey ::= CHOICE { 
    eciesNistP256         EccP256CurvePoint,
    eciesBrainpoolP256r1  EccP256CurvePoint,
    ...
  }

/** 
 * @class PublicVerificationKey
 *
 * @brief This structure represents a public key and states with what
 * algorithm the public key is to be used. Cryptographic mechanisms are
 * defined in 5.3.
 *
 * <br><br>An EccP256CurvePoint or EccP384CurvePoint within a
 * PublicVerificationKey structure is invalid if it indicates the choice
 * x-only. 
 *
 * <br><br><b>Critical information fields</b>: If present, this is a critical
 * information field as defined in 5.2.6. An implementation that does not
 * recognize the indicated CHOICE when verifying a signed SPDU shall indicate
 * that the signed SPDU is invalid. 
 */
  PublicVerificationKey ::= CHOICE { 
    ecdsaNistP256         EccP256CurvePoint,
    ecdsaBrainpoolP256r1  EccP256CurvePoint,
    ...,
    ecdsaBrainpoolP384r1  EccP384CurvePoint,
    ecdsaNistP384         EccP384CurvePoint
  }

/** 
 * @class SymmetricEncryptionKey
 *
 * @brief This structure provides the key bytes for use with an identified
 * symmetric algorithm. The only supported symmetric algorithm is AES-128 in
 * CCM mode as specified in 5.3.7.
 */
  SymmetricEncryptionKey ::= CHOICE {
    aes128Ccm  OCTET STRING(SIZE(16)),
    ...
  }


--***************************************************************************--
--                              PSID / ITS-AID                               --
--***************************************************************************--

/** 
 * @class PsidSsp 
 *
 * @brief This structure represents the permissions that the certificate
 * holder has with respect to data for a single application area, identified
 * by a Psid. If the ServiceSpecificPermissions field is omitted, it
 * indicates that the certificate holder has the default permissions
 * associated with that Psid. 
 *
 * <br><br><b>Consistency with signed SPDU</b>. As noted in 5.1.1,
 * consistency between the SSP and the signed SPDU is defined by rules
 * specific to the given PSID and is out of scope for this standard.
 *
 * <br><br><b>Consistency with issuing certificate</b>. 
 *
 * <br><br>If a certificate has an appPermissions entry A for which the ssp
 * field is omitted, A is consistent with the issuing certificate if the
 * issuing certificate contains a PsidSspRange P for which the following holds:
 * <ul>
 * <li> The psid field in P is equal to the psid field in A and one of the
 * following is true:</li>
 * <ul>
 * <li> The sspRange field in P indicates all.</li>
 *
 * <li> The sspRange field in P indicates opaque and one of the entries in
 * opaque is an OCTET STRING of length 0.</li>
 * </ul>
 * </ul>
 *
 * For consistency rules for other forms of the ssp field, see the
 * following subclauses.
 */
  PsidSsp ::= SEQUENCE {
    psid  Psid,
    ssp   ServiceSpecificPermissions OPTIONAL
  }

/** 
 * @class SequenceOfPsidSsp
 *
 * @brief This type is used for clarity of definitions.
 */
  SequenceOfPsidSsp ::= SEQUENCE OF PsidSsp

/** 
 * @class Psid
 *
 * @brief This type represents the PSID defined in IEEE Std 1609.12.
 */
  Psid ::= INTEGER (0..MAX)

/** 
 * @class SequenceOfPsid
 *
 * @brief This type is used for clarity of definitions. 
 */
  SequenceOfPsid ::= SEQUENCE OF Psid

/** 
 * @class ServiceSpecificPermissions
 *
 * @brief This structure represents the Service Specific Permissions (SSP)
 * relevant to a given entry in a PsidSsp. The meaning of the SSP is specific
 * to the associated Psid. SSPs may be PSID-specific octet strings or
 * bitmap-based. See Annex C for further discussion of how application
 * specifiers may choose which SSP form to use.
 *
 * <br><br><b>Consistency with issuing certificate</b>. 
 *
 * <br><br>If a certificate has an appPermissions entry A for which the ssp
 * field is opaque, A is consistent with the issuing certificate if the
 * issuing certificate contains one of the following:
 * <ul>
 * <li> (OPTION 1) A SubjectPermissions field indicating the choice all and
 * no PsidSspRange field containing the psid field in A;</li>
 * 
 * <li> (OPTION 2) A PsidSspRange P for which the following holds:</li>
 * <ul>
 * <li> The psid field in P is equal to the psid field in A and one of the
 * following is true:</li>
 * <ul>
 * <li> The sspRange field in P indicates all.</li>
 * 
 * <li> The sspRange field in P indicates opaque and one of the entries in
 * the opaque field in P is an OCTET STRING identical to the opaque field in
 * A.</li>
 * </ul>
 * </ul>
 * </ul>
 * 
 * For consistency rules for other types of ServiceSpecificPermissions,
 * see the following subclauses.
 */
  ServiceSpecificPermissions ::= CHOICE {
    opaque     OCTET STRING (SIZE(0..MAX)),
    ...,
    bitmapSsp  BitmapSsp
  }

/** 
 * @class BitmapSsp
 *
 * @brief This structure represents a bitmap representation of a SSP. The
 * mapping of the bits of the bitmap to constraints on the signed SPDU is
 * PSID-specific.
 *
 * <br><br><b>Consistency with issuing certificate</b>. 
 *
 * <br><br>If a certificate has an appPermissions entry A for which the ssp
 * field is bitmapSsp, A is consistent with the issuing certificate if the
 * issuing certificate contains one of the following:
 * <ul>
 * <li> (OPTION 1) A SubjectPermissions field indicating the choice all and
 * no PsidSspRange field containing the psid field in A;</li>
 * 
 * <li> (OPTION 2) A PsidSspRange P for which the following holds:</li>
 * <ul>
 * <li> The psid field in P is equal to the psid field in A and one of the
 * following is true:</li>
 * <ul>
 * <li> EITHER The sspRange field in P indicates all</li>
 *
 * <li> OR The sspRange field in P indicates bitmapSspRange and for every
 * bit set to 1 in the sspBitmask in P, the bit in the identical position in
 * the sspValue in A is set equal to the bit in that position in the
 * sspValue in P.</li>
 * </ul>
 * </ul>
 * </ul>
 *
 * NOTE: A BitmapSsp B is consistent with a BitmapSspRange R if for every
 * bit set to 1 in the sspBitmask in R, the bit in the identical position in
 * B is set equal to the bit in that position in the sspValue in R. For each
 * bit set to 0 in the sspBitmask in R, the corresponding bit in the
 * identical position in B may be freely set to 0 or 1, i.e., if a bit is
 * set to 0 in the sspBitmask in R, the value of corresponding bit in the
 * identical position in B has no bearing on whether B and R are consistent.
 */
  BitmapSsp ::= OCTET STRING (SIZE(0..31))

/** 
 * @class PsidSspRange
 *
 * @brief This structure represents the certificate issuing or requesting
 * permissions of the certificate holder with respect to one particular set
 * of application permissions.
 *
 * @param psid identifies the application area.
 *
 * @param sspRange identifies the SSPs associated with that PSID for which
 * the holder may issue or request certificates. If sspRange is omitted, the
 * holder may issue or request certificates for any SSP for that PSID.
 */
  PsidSspRange ::= SEQUENCE {
    psid      Psid,
    sspRange  SspRange OPTIONAL
  }

/** 
 * @class SequenceOfPsidSspRange
 *
 * @brief This type is used for clarity of definitions.
 */
  SequenceOfPsidSspRange ::= SEQUENCE OF PsidSspRange

/** 
 * @class SspRange
 *
 * @brief This structure identifies the SSPs associated with a PSID for
 * which the holder may issue or request certificates. 
 *
 * <br><br><b>Consistency with issuing certificate</b>. 
 * 
 * <br><br>If a certificate has a PsidSspRange A for which the ssp field is
 * opaque, A is consistent with the issuing certificate if the issuing
 * certificate contains one of the following:
 * <ul>
 * <li> (OPTION 1) A SubjectPermissions field indicating the choice all and
 * no PsidSspRange field containing the psid field in A;</li>
 *
 * <li> (OPTION 2) a PsidSspRange P for which the following holds:</li>
 * <ul>
 * <li> The psid field in P is equal to the psid field in A and one of the
 * following is true:</li>
 * <ul>
 * <li> The sspRange field in P indicates all.</li>
 *
 * <li> The sspRange field in P indicates opaque, and the sspRange field in
 * A indicates opaque, and every OCTET STRING within the opaque in A is a
 * duplicate of an OCTET STRING within the opaque in P.</li>
 * </ul>
 * </ul>
 * </ul>
 *
 * If a certificate has a PsidSspRange A for which the ssp field is all,
 * A is consistent with the issuing certificate if the issuing certificate
 * contains a PsidSspRange P for which the following holds:
 * <ul>
 * <li> (OPTION 1) A SubjectPermissions field indicating the choice all and
 * no PsidSspRange field containing the psid field in A;</li>
 *
 * <li>(OPTION 2) A PsidSspRange P for which the psid field in P is equal to
 * the psid field in A and the sspRange field in P indicates all.</li>
 * </ul>
 *
 * For consistency rules for other types of SspRange, see the following
 * subclauses.
 *
 * <br><br>NOTE: The choice "all" may also be indicated by omitting the
 * SspRange in the enclosing PsidSspRange structure. Omitting the SspRange is
 * preferred to explicitly indicating "all".
 */
  SspRange ::= CHOICE {
    opaque          SequenceOfOctetString,
    all             NULL,
    ... ,
    bitmapSspRange  BitmapSspRange
  }
   
/** 
 * @class BitmapSspRange
 *
 * @brief This structure represents a bitmap representation of a SSP. The
 * sspValue indicates permissions. The sspBitmask contains an octet string
 * used to permit or constrain sspValue fields in issued certificates. The
 * sspValue and sspBitmask fields shall be of the same length.
 *
 * <br><br><b>Consistency with issuing certificate</b>. 
 *
 * <br><br>If a certificate has an PsidSspRange value P for which the
 * sspRange field is bitmapSspRange, P is consistent with the issuing
 * certificate if the issuing certificate contains one of the following:
 * <ul>
 * <li> (OPTION 1) A SubjectPermissions field indicating the choice all and
 * no PsidSspRange field containing the psid field in P;</li>
 *
 * <li> (OPTION 2) A PsidSspRange R for which the following holds:</li>
 * <ul>
 * <li> The psid field in R is equal to the psid field in P and one of the
 * following is true:</li>
 * <ul>
 * <li> EITHER The sspRange field in R indicates all</li>
 *
 * <li> OR The sspRange field in R indicates bitmapSspRange and for every
 * bit set to 1 in the sspBitmask in R:</li>
 * <ul>
 * <li> The bit in the identical position in the sspBitmask in P is set
 * equal to 1, AND</li>
 *
 * <li> The bit in the identical position in the sspValue in P is set equal
 * to the bit in that position in the sspValue in R.</li>
 * </ul>
 * </ul>
 * </ul>
 * </ul>
 *
 * <br>Reference ETSI TS 103 097 [B7] for more information on bitmask SSPs.
 */
  BitmapSspRange ::= SEQUENCE {
    sspValue    OCTET STRING (SIZE(1..32)),
    sspBitmask  OCTET STRING (SIZE(1..32))
  }

/** 
 * @class SequenceOfOctetString
 *
 * @brief This type is used for clarity of definitions.
 */
  SequenceOfOctetString ::= 
    SEQUENCE (SIZE (0..MAX)) OF OCTET STRING (SIZE(0..MAX))


--***************************************************************************--
--                          Certificate Components                           --
--***************************************************************************--

/** 
 * @class SubjectAssurance
 *
 * @brief This field contains the certificate holder’s assurance level, which
 * indicates the security of both the platform and storage of secret keys as
 * well as the confidence in this assessment.
 *
 * <br><br>This field is encoded as defined in Table 1, where "A" denotes bit
 * fields specifying an assurance level, "R" reserved bit fields, and "C" bit
 * fields specifying the confidence. 
 *
 * <br><br>Table 1: Bitwise encoding of subject assurance
 *
 * <table>
 * <tr>
 * <td><b>Bit number</b></td> <td>7</td> <td>6</td> <td>5</td> <td>4</td>
 * <td>3</td> <td>2</td> <td>1</td> <td>0</td>
 * </tr>
 * <tr>
 * <td><b>Interpretation</b></td> <td>A</td> <td>A</td> <td>A</td> <td>R</td>
 * <td>R</td> <td>R</td> <td>C</td> <td>C</td>
 * </tr>
 * </table>
 *
 * In Table 1, bit number 0 denotes the least significant bit. Bit 7
 * to bit 5 denote the device's assurance levels, bit 4 to bit 2 are reserved
 * for future use, and bit 1 and bit 0 denote the confidence.
 *
 * <br><br>The specification of these assurance levels as well as the
 * encoding of the confidence levels is outside the scope of the present
 * document. It can be assumed that a higher assurance value indicates that
 * the holder is more trusted than the holder of a certificate with lower
 * assurance value and the same confidence value. 
 *
 * <br><br>NOTE: This field was originally specified in ETSI TS 103 097 [B7]
 * and future uses of this field are anticipated to be consistent with future
 * versions of that document.
 */
  SubjectAssurance ::= OCTET STRING (SIZE(1))

/** 
 * @class CrlSeries
 *
 * @brief This integer identifies a series of CRLs issued under the authority
 * of a particular CRACA.
 */
  CrlSeries ::= Uint16


--***************************************************************************--
--                             Pseudonym Linkage                             --
--***************************************************************************--
  
/** 
 * @class IValue
 *
 * @brief This atomic type is used in the definition of other data structures.
 */
  IValue ::= Uint16
  
/** 
 * @class Hostname
 *
 * @brief This is a UTF-8 string as defined in IETF RFC 3629. The contents
 * are determined by policy.
 */
  Hostname ::= UTF8String (SIZE(0..255))
  
/** 
 * @class LinkageValue
 *
 * @brief This is the individual linkage value. See 5.1.3 and 7.3 for details
 * of use.
 */
  LinkageValue ::= OCTET STRING (SIZE(9))
  
/** 
 * @class GroupLinkageValue
 *
 * @brief This is the group linkage value. See 5.1.3 and 7.3 for details of
 * use.
 */
  GroupLinkageValue ::= SEQUENCE {
    jValue  OCTET STRING (SIZE(4)),
    value   OCTET STRING (SIZE(9))
  }
  
/** 
 * @class LaId
 *
 * @brief This structure contains a LA Identifier for use in the algorithms
 * specified in 5.1.3.4.
 */
  LaId ::= OCTET STRING (SIZE(2)) 
  
/** 
 * @class LinkageSeed
 *
 * @brief This structure contains a linkage seed value for use in the
 * algorithms specified in 5.1.3.4.
 */
  LinkageSeed ::= OCTET STRING (SIZE(16))

END

--***************************************************************************--
--                        IEEE Std 1609.2: Data Types                        --
--***************************************************************************--

/** 
 * @brief NOTE: Section references in this file are to clauses in IEEE Std
 * 1609.2 unless indicated otherwise. Full forms of acronyms and
 * abbreviations used in this file are specified in 3.2. 
 */
 
Ieee1609Dot2 {iso(1) identified-organization(3) ieee(111) 
  standards-association-numbered-series-standards(2) wave-stds(1609)  
  dot2(2) base (1) schema (1) major-version-2(2) minor-version-4(4)}

DEFINITIONS AUTOMATIC TAGS ::= BEGIN 
 
EXPORTS ALL;

IMPORTS 
  CrlSeries,
  EccP256CurvePoint,
  EciesP256EncryptedKey,
  EncryptionKey,
  GeographicRegion,
  GroupLinkageValue,
  HashAlgorithm,
  HashedId3,
  HashedId8,
  Hostname,
  IValue,
  LinkageValue,
  Opaque,
  Psid,
  PsidSsp,
  PsidSspRange,
  PublicEncryptionKey,
  PublicVerificationKey,
  SequenceOfHashedId3,
  SequenceOfPsidSsp,
  SequenceOfPsidSspRange,
  ServiceSpecificPermissions,
  Signature,
  SubjectAssurance,
  SymmetricEncryptionKey,
  ThreeDLocation,
  Time64,
  Uint3,
  Uint8,
  Uint16, 
  Uint32,
  ValidityPeriod
FROM Ieee1609Dot2BaseTypes {iso(1) identified-organization(3) ieee(111) 
  standards-association-numbered-series-standards(2) wave-stds(1609) dot2(2)
  base(1) base-types(2) major-version-2(2) minor-version-3(3)}
/* WITH Successors */

EtsiOriginatingHeaderInfoExtension 
FROM EtsiTs103097ExtensionModule {itu-t(0) identified-organization(4)
    etsi(0) itsDomain(5) wg5(5) secHeaders(103097) extension(2)
    version-1(1) minor-version-1(1)}
/* WITH Successors */
;

--***************************************************************************--
--                               Secured Data                                --
--***************************************************************************--

/** 
 * @class Ieee1609Dot2Data 
 *
 * @brief This data type is used to contain the other data types in this
 * clause. The fields in the Ieee1609Dot2Data have the following meanings:  
 *
 * @param protocolVersion contains the current version of the protocol. The
 * version specified in this document is version 3, represented by the
 * integer 3. There are no major or minor version numbers.
 *
 * @param content contains the content in the form of an Ieee1609Dot2Content.
 */
  Ieee1609Dot2Data ::= SEQUENCE {
    protocolVersion  Uint8(3),
    content          Ieee1609Dot2Content
  }

/**
 * @class Ieee1609Dot2Content
 * 
 * @brief In this structure:
 *
 * @param unsecuredData indicates that the content is an OCTET STRING to be
 * consumed outside the SDS.
 *
 * @param signedData indicates that the content has been signed according to
 * this standard.
 *
 * @param encryptedData indicates that the content has been encrypted
 * according to this standard.
 *
 * @param signedCertificateRequest indicates that the content is a
 * certificate request. Further specification of certificate requests is not
 * provided in this version of this standard.
 */
  Ieee1609Dot2Content ::=  CHOICE { 
    unsecuredData             Opaque, 
    signedData                SignedData,
    encryptedData             EncryptedData,
    signedCertificateRequest  Opaque,
    ...,
    signedX509CertificateRequest  Opaque
  }

/**
 * @class SignedData
 * 
 * @brief In this structure:
 *
 * @param hashId indicates the hash algorithm to be used to generate the hash
 * of the message for signing and verification.
 *
 * @param tbsData contains the data that is hashed as input to the signature.
 *
 * @param signer determines the keying material and hash algorithm used to
 * sign the data.
 *
 * @param signature contains the digital signature itself, calculated as
 * specified in 5.3.1.
 * <ul>
 * <li> If signer indicates the choice self, then the signature calculation
 * is parameterized as follows:</li>
 * <ul>
 * <li> <i>Data input</i> is equal to the COER encoding of the tbsData field
 * canonicalized according to the encoding considerations given in 6.3.6.</li>
 *
 * <li> <i>Verification type</i> is equal to <i>self</i>.</li>
 *
 * <li> <i>Signer identifier input</i> is equal to the empty string.</li>
 * </ul>
 *
 * <li> If signer indicates certificate or digest, then the signature
 * calculation is parameterized as follows:</li>
 * <ul>
 * <li> <i>Data input</i> is equal to the COER encoding of the tbsData field
 * canonicalized according to the encoding considerations given in 6.3.6.</li>
 *
 * <li> <i>Verification type</i> is equal to <i>certificate</i>.</li>
 *
 * <li> <i>Signer identifier input</i> equal to the COER-encoding of the
 * Certificate that is to be used to verify the SPDU, canonicalized according
 * to the encoding considerations given in 6.4.3.</li>
 * </ul>
 * </ul>
 */
  SignedData ::= SEQUENCE { 
    hashId     HashAlgorithm,
    tbsData    ToBeSignedData,
    signer     SignerIdentifier,
    signature  Signature
  }

/**
 * @class ToBeSignedData
 * 
 * @brief This structure contains the data to be hashed when generating or
 * verifying a signature. See 6.3.4 for the specification of the input to the
 * hash.
 * 
 * <br><br><b>Encoding considerations</b>: For encoding considerations
 * associated with the headerInfo field, see 6.3.9.
 *
 * <br><br><b>Parameters</b>:
 *
 * @param payload contains data that is provided by the entity that invokes
 * the SDS.
 *
 * @param headerInfo contains additional data that is inserted by the SDS. 
 */
  ToBeSignedData ::= SEQUENCE { 
    payload     SignedDataPayload,
    headerInfo  HeaderInfo
  }

/**
 * @class SignedDataPayload
 * 
 * @brief This structure contains the data payload of a ToBeSignedData. This
 * structure contains at least one of data and extDataHash, and may contain
 * both.
 *
 * @param data contains data that is explicitly transported within the
 * structure.
 *
 * @param extDataHash contains the hash of data that is not explicitly
 * transported within the structure, and which the creator of the structure
 * wishes to cryptographically bind to the signature. For example, if a
 * creator wanted to indicate that some large message was still valid, they
 * could use the extDataHash field to send a SignedÂ¬Data containing the hash
 * of that large message without having to resend the message itself. Whether
 * or not extDataHash is used, and how it is used, is SDEE-specific. 
 */  
  SignedDataPayload ::= SEQUENCE { 
    data         Ieee1609Dot2Data OPTIONAL,
    extDataHash  HashedData OPTIONAL,
    ...
  } (WITH COMPONENTS {..., data PRESENT} | 
     WITH COMPONENTS {..., extDataHash PRESENT})

/**
 * @class HashedData
 * 
 * @brief This structure contains the hash of some data with a specified hash
 * algorithm. The hash algorithms supported in this version of this
 * standard are SHA-256 (in the root) and SHA-384 (in the first extension).
 * The reserved extension is for future use.
 *
 * <br><br><b>Critical information fields</b>: If present, this is a critical
 * information field as defined in 5.2.6. An implementation that does not
 * recognize the indicated CHOICE for this type when verifying a signed SPDU
 * shall indicate that the signed SPDU is invalid.
 */
  HashedData::= CHOICE { 
    sha256HashedData  OCTET STRING (SIZE(32)),
    ...,
    sha384HashedData  OCTET STRING (SIZE(48)),
    reserved          OCTET STRING (SIZE(32))
  }

/**
 * @class HeaderInfo
 * 
 * @brief This structure contains information that is used to establish
 * validity by the criteria of 5.2.
 *
 * <br><br><b>Encoding considerations</b>: When the structure is encoded in
 * order to be digested to generate or check a signature, if encryptionKey is
 * present, and indicates the choice public, and contains a
 * BasePublicEncryptionKey that is an elliptic curve point (i.e., of
 * typeEccP256CurvePoint or EccP384CurvePoint), then the elliptic curve point
 * is encoded in compressed form, i.e., such that the choice indicated within
 * the Ecc*CurvePoint is compressed-y-0 or compressed-y-1.
 *
 * <br><br><b>Parameters</b>:
 *
 * @param psid indicates the application area with which the sender is
 * claiming the payload should be associated.
 *
 * @param generationTime indicates the time at which the structure was
 * generated. See 5.2.5.2.2 and 5.2.5.2.3 for discussion of the use of this
 * field. 
 *
 * @param expiryTime, if present, contains the time after which the data
 * should no longer be considered relevant. If both generationTime and
 * expiryTime are present, the signed SPDU is invalid if generationTime is
 * not strictly earlier than expiryTime.
 *
 * @param generationLocation, if present, contains the location at which the
 * signature was generated. 
 *
 * @param p2pcdLearningRequest, if present, is used by the SDS to request
 * certificates for which it has seen identifiers but does not know the
 * entire certificate. A specification of this peer-to-peer certificate
 * distribution (P2PCD) mechanism is given in Clause 8. This field is used
 * for the out-of-band flavor of P2PCD and shall only be present if
 * inlineP2pcdRequest is not present. The HashedId3 is calculated with the
 * whole-certificate hash algorithm, determined as described in 6.4.3.
 *
 * @param missingCrlIdentifier, if present, is used by the SDS to request
 * CRLs which it knows to have been issued but have not received. This is
 * provided for future use and the associated mechanism is not defined in
 * this version of this standard.
 *
 * @param encryptionKey, if present, is used to indicate that a further
 * communication should be encrypted with the indicated key. One possible use
 * of this key to encrypt a response is specified in 6.3.35, 6.3.37, and
 * 6.3.34. An encryptionKey field of type symmetric should only be used if
 * the SignedÂ¬Data containing this field is securely encrypted by some means. 
 *
 * @param inlineP2pcdRequest, if present, is used by the SDS to request
 * unknown certificates per the inline peer-to-peer certificate distribution
 * mechanism is given in Clause 8. This field shall only be present if
 * p2pcdLearningRequest is not present. The HashedId3 is calculated with the
 * whole-certificate hash algorithm, determined as described in 6.4.3.
 *
 * @param requestedCertificate, if present, is used by the SDS to provide
 * certificates per the âinlineâ? version of the peer-to-peer certificate
 * distribution mechanism given in Clause 8.
 *
 * @param pduFunctionalType, if present, is used to indicate that the SPDU is
 * to be consumed by a process other than an application process as defined
 * in ISO 21177 [B14a]. See 6.3.23b for more details.
 *
 * @param contributedExtensions, if present, is used to provide extension blocks
 * defined by identified contributing organizations.
 */
  HeaderInfo ::= SEQUENCE { 
    psid                  Psid,
    generationTime        Time64 OPTIONAL,
    expiryTime            Time64  OPTIONAL,
    generationLocation    ThreeDLocation OPTIONAL,
    p2pcdLearningRequest  HashedId3 OPTIONAL,
    missingCrlIdentifier  MissingCrlIdentifier OPTIONAL,
    encryptionKey         EncryptionKey OPTIONAL,
    ...,
    inlineP2pcdRequest    SequenceOfHashedId3 OPTIONAL,
    requestedCertificate  Certificate OPTIONAL,
    pduFunctionalType     PduFunctionalType OPTIONAL,
    contributedExtensions ContributedExtensionBlocks OPTIONAL
  }

/**
 * @class MissingCrlIdentifier
 * 
 * @brief This structure may be used to request a CRL that the SSME knows to
 * have been issued but has not yet received. It is provided for future use
 * and its use is not defined in this version of this standard.
 *
 * @param cracaId is the HashedId3 of the CRACA, as defined in 5.1.3. The
 * HashedId3 is calculated with the whole-certificate hash algorithm,
 * determined as described in 6.4.3.
 *
 * @param crlSeries is the requested CRL Series value. See 5.1.3 for more
 * information.
 */
  MissingCrlIdentifier ::= SEQUENCE { 
    cracaId    HashedId3,
	crlSeries  CrlSeries,
	...
  }

/**
 * @class PduFunctionalType
 * 
 * @brief This data structure identifies the functional entity that is
 * intended to consume an SPDU, for the case where that functional entity is
 * not an application process but security support services for an
 * application process. Further details and the intended use of this field
 * are defined in ISO 21177 [B14a]. 
 *
 * <br><br>An SPDU in which the pduFunctionalType field is present conforms
 * to the security profile for that PduFunctionalType value (given in ISO
 * 21177 [B14a]), not to the security profile for Application SPDUs for the
 * PSID.
 *
 * @param tlsHandshake indicates that the Signed SPDU is not to be directly
 * consumed as an application PDU but is to be used to provide information
 * about the holderâs permissions to a Transport Layer Security (TLS) (IETF
 * 5246 [B13], IETF 8446 [B13a]) handshake process operating to secure
 * communications to an application process. See IETF [B13b] and ISO 21177
 * [B14a] for further information.
 *
 * @param iso21177ExtendedAuth indicates that the Signed SPDU is not to be
 * directly consumed as an application PDU but is to be used to provide
 * additional information about the holderâs permissions to the ISO 21177
 * Security Subsystem for an application process. See ISO 21177 [B14a] for
 * further information.
 */
  PduFunctionalType ::= INTEGER (0..255)
    tlsHandshake          PduFunctionalType ::= 1
    iso21177ExtendedAuth  PduFunctionalType ::= 2

/**
 * @class ContributedExtensionBlocks 
 * 
 * @brief This data structure defines a list of ContributedExtensionBlock
 */
  ContributedExtensionBlocks ::= SEQUENCE (SIZE(1..MAX)) OF ContributedExtensionBlock

/**
 * @class ContributedExtensionBlock 
 * 
 * @brief This data structure defines the format of an extension block 
 * provided by an identified contributor by using the temnplate provided
 * in the class IEEE1609DOT2-HEADERINFO-CONTRIBUTED-EXTENSION constraint
 * to the objects in the set Ieee1609Dot2HeaderInfoContributedExtensions.
 *
 * @param contributorId uniquely identifies the contributor
 *
 * @param extns contains a list of extensions from that contributor.   
 */
 /* ContributedExtensionBlock ::= SEQUENCE {
      contributorId IEEE1609DOT2-HEADERINFO-CONTRIBUTED-EXTENSION.
              &id({Ieee1609Dot2HeaderInfoContributedExtensions}),
      extns   SEQUENCE (SIZE(1..MAX)) OF IEEE1609DOT2-HEADERINFO-CONTRIBUTED-EXTENSION.
              &Extn({Ieee1609Dot2HeaderInfoContributedExtensions}{@.contributorId})
}*/
ContributedExtensionBlock ::= SEQUENCE {
      contributorId NULL
}

/**
 * @class IEEE1609DOT2-HEADERINFO-CONTRIBUTED-EXTENSION
 * 
 * @brief This data structure defines the information object class that 
 * provides a "template" for defining extension blocks.
 */
 /* IEEE1609DOT2-HEADERINFO-CONTRIBUTED-EXTENSION ::= CLASS {
      &id    HeaderInfoContributorId UNIQUE,
      &Extn
  } WITH SYNTAX {&Extn IDENTIFIED BY &id} */

  IEEE1609DOT2-HEADERINFO-CONTRIBUTED-EXTENSION ::= SEQUENCE {
      id NULL
  }
  
/**
 * @class Ieee1609Dot2HeaderInfoContributedExtensions
 * 
 * @brief This data structure defines the set of ContributedExtensionBlock 
 * Objects. 
 *
 * @param In this version of the standard, only the type
 * EtsiOriginatingHeaderInfoExtension contributed by ETSI is supported.
 * The information object EtsiOriginatingHeaderInfoExtension is imported 
 * from the EtsiTs103097ExtensionModule 
 */
  Ieee1609Dot2HeaderInfoContributedExtensions 
      IEEE1609DOT2-HEADERINFO-CONTRIBUTED-EXTENSION ::= {
      {EtsiOriginatingHeaderInfoExtension IDENTIFIED BY etsiHeaderInfoContributorId},
      ...
  }

/**
 * @class HeaderInfoContributorId 
 * 
 * @brief This data structure defines the header info contributor id type 
 * and its values. 
 *
 * @param In this version of the standard, value 2 is assigned to ETSI.
 */
  HeaderInfoContributorId ::= INTEGER (0..255)
      etsiHeaderInfoContributorId         HeaderInfoContributorId ::= 2

/**
 * @class SignerIdentifier
 * 
 * @brief This structure allows the recipient of data to determine which
 * keying material to use to authenticate the data. It also indicates the
 * verification type to be used to generate the hash for verification, as
 * specified in 5.3.1. 
 * <ul>
 * <li> If the choice indicated is digest:</li>
 * <ul>
 * <li> The structure contains the HashedId8 of the relevant certificate. The
 * HashedId8 is calculated with the whole-certificate hash algorithm,
 * determined as described in 6.4.3.</li>
 *
 * <li> The verification type is <i>certificate</i> and the certificate data
 * passed to the hash function as specified in 5.3.1 is the authorization
 * certificate.</li>
 * </ul>
 *
 * <li> If the choice indicated is certificate:</li> 
 * <ul>
 * <li> The structure contains one or more Certificate structures, in order
 * such that the first certificate is the authorization certificate and each
 * subsequent certificate is the issuer of the one before it.</li>
 *
 * <li> The verification type is <i>certificate</i> and the certificate data
 * passed to the hash function as specified in 5.3.1 is the authorization
 * certificate.</li> 
 * </ul>
 *
 * <li> If the choice indicated is self:</li>
 * <ul>
 * <li> The structure does not contain any data beyond the indication that
 * the choice value is self.</li>
 *
 * <li> The verification type is <i>self-signed</i>.</li>
 * </ul>
 * </ul>
 *
 * <b>Critical information fields</b>:
 * <ol>
 * <li> If present, this is a critical information field as defined in 5.2.6.
 * An implementation that does not recognize the CHOICE value for this type
 * when verifying a signed SPDU shall indicate that the signed SPDU is invalid.
 * </li>
 *
 * <li> If present, certificate is a critical information field as defined in
 * 5.2.6. An implementation that does not support the number of certificates
 * in certificate when verifying a signed SPDU shall indicate that the signed
 * SPDU is invalid. A compliant implementation shall support certificate
 * fields containing at least one certificate.</li>
 * </ol>
 */ 
  SignerIdentifier ::= CHOICE { 
    digest       HashedId8,
    certificate  SequenceOfCertificate,
    self         NULL,
    ...
  }

--***************************************************************************--
--                              Encrypted Data                               --
--***************************************************************************--

/**
 * @class EncryptedData
 * 
 * @brief This data structure encodes data that has been encrypted to one or
 * more recipients using the recipientsâ public or symmetric keys as
 * specified in 1.1.1.
 *
 * <br><br><b>Critical information fields</b>:
 * <ul>
 * <li> If present, recipients is a critical information field as defined in
 * 5.2.6. An implementation that does not support the number of RecipientInfo
 * in recipients when decrypted shall indicate that the encrypted SPDU could
 * not be decrypted due to unsupported critical information fields. A
 * compliant implementation shall support recipients fields containing at
 * least eight entries.</li>
 * </ul>
 *
 * <b>Parameters</b>:
 * 
 * @param recipients contains one or more RecipientInfos. These entries may
 * be more than one RecipientInfo, and more than one type of RecipientInfo,
 * as long as they are all indicating or containing the same data encryption
 * key.
 *
 * @param ciphertext contains the encrypted data. This is the encryption of
 * an encoded Ieee1609Dot2Data structure as specified in 5.3.4.2.
 */
  EncryptedData ::= SEQUENCE { 
    recipients  SequenceOfRecipientInfo,
	ciphertext  SymmetricCiphertext
  }

/**
 * @class RecipientInfo
 * 
 * @brief This data structure is used to transfer the data encryption key to
 * an individual recipient of an EncryptedData. The option pskRecipInfo is
 * selected if the EncryptedData was encrypted using the static encryption
 * key approach specified in 1.1.1.1. The other options are selected if the
 * EncryptedData was encrypted using the ephemeral encryption key approach
 * specified in 1.1.1.1. The meanings of the choices are:
 *
 * <br><br>See Annex C.7 for guidance on when it may be appropriate to use
 * each of these approaches.
 *
 * @param pskRecipInfo: The ciphertext was encrypted directly using a
 * symmetric key.
 *
 * @param symmRecipInfo: The data encryption key was encrypted using a
 * symmetric key.
 *
 * @param certRecipInfo: The data encryption key was encrypted using a public
 * key encryption scheme, where the public encryption key was obtained from a
 * certificate. In this case, the parameter P1 to ECIES as defined in 5.3.4
 * is the hash of the certificate.
 *
 * @param signedDataRecipInfo: The data encryption key was encrypted using a
 * public encryption key, where the encryption key was obtained as the public
 * response encryption key from a Signed-Data. In this case, the parameter P1
 * to ECIES as defined in 5.3.4 is the SHA-256 hash of the Ieee1609Dot2Data
 * containing the response encryption key.
 *
 * @param rekRecipInfo: The data encryption key was encrypted using a public
 * key that was not obtained from a SignedÂ¬Data. In this case, the parameter
 * P1 to ECIES as defined in 5.3.4 is the hash of the empty string.
 */
  RecipientInfo ::= CHOICE { 
    pskRecipInfo         PreSharedKeyRecipientInfo,
    symmRecipInfo        SymmRecipientInfo,
    certRecipInfo        PKRecipientInfo, 
    signedDataRecipInfo  PKRecipientInfo, 
    rekRecipInfo         PKRecipientInfo 
  }

/** 
 * @class SequenceOfRecipientInfo
 *
 * @brief This type is used for clarity of definitions.
 */
  SequenceOfRecipientInfo ::= SEQUENCE OF RecipientInfo
  
/** 
 * @class PreSharedKeyRecipientInfo
 *
 * @brief This data structure is used to indicate a symmetric key that may be
 * used directly to decrypt a SymmetricCiphertext. It consists of the
 * low-order 8 bytes of the SHA-256 hash of the COER encoding of a
 * SymmetricEncryptionKey structure containing the symmetric key in question.
 * The symmetric key may be established by any appropriate means agreed by
 * the two parties to the exchange.         
 */
  PreSharedKeyRecipientInfo ::= HashedId8
  
/** 
 * @class SymmRecipientInfo
 *
 * @brief This data structure contains the following fields:
 *
 * @param recipientId contains the hash of the symmetric key encryption key
 * that may be used to decrypt the data encryption key. It consists of the
 * low-order 8 bytes of the SHA-256 hash of the COER encoding of a
 * SymmetricEncryptionKey structure containing the symmetric key in question.
 * The symmetric key may be established by any appropriate means agreed by
 * the two parties to the exchange.
 *
 * @param encKey contains the encrypted data encryption key within an AES-CCM
 * ciphertext.
 */
  SymmRecipientInfo ::= SEQUENCE { 
    recipientId  HashedId8, 
    encKey       SymmetricCiphertext
  }

/** 
 * @class PKRecipientInfo
 *
 * @brief This data structure contains the following fields:
 *
 * @param recipientId contains the hash of the container for the encryption
 * public key as specified in the definition of RecipientInfo. Specifically,
 * depending on the choice indicated by the containing RecipientInfo structure:
 * <ul>
 * <li> If the containing RecipientInfo structure indicates certRecipInfo,
 * this field contains the HashedId8 of the certificate. The HashedId8 is
 * calculated with the whole-certificate hash algorithm, determined as
 * described in 6.4.3.</li>
 *
 * <li> If the containing RecipientInfo structure indicates
 * signedDataRecipInfo, this field contains the HashedId8 of the
 * Ieee1609Dot2Data of type signed that contained the encryption key, with
 * that Ieee1609Dot2Data canonicalized per 6.3.4. The HashedId8 is calculated
 * with SHA-256.</li>
 *
 * <li> If the containing RecipientInfo structure indicates rekRecipInfo,
 * this field contains the HashedId8 of the COER encoding of a
 * PublicEncryptionKey structure containing the response encryption key. The
 * HashedId8 is calculated with SHA-256.</li>
 * </ul>
 *
 * @param encKey contains the encrypted key. 
 */
  PKRecipientInfo ::= SEQUENCE { 
    recipientId  HashedId8, 
    encKey       EncryptedDataEncryptionKey
  }

/** 
 * @class EncryptedDataEncryptionKey
 *
 * @brief This data structure contains an encrypted data encryption key. 
 *
 * <br><br><b>Critical information fields</b>: If present and applicable to
 * the receiving SDEE, this is a critical information field as defined in
 * 5.2.6. If an implementation receives an encrypted SPDU and determines that
 * one or more RecipientInfo fields are relevant to it, and if all of those
 * RecipientInfos contain an EncryptedDataEncryptionKey such that the
 * implementation does not recognize the indicated CHOICE, the implementation
 * shall indicate that the encrypted SPDU is not decryptable.
 */
  EncryptedDataEncryptionKey ::= CHOICE { 
    eciesNistP256         EciesP256EncryptedKey,
    eciesBrainpoolP256r1  EciesP256EncryptedKey,
    ...
  }

/** 
 * @class SymmetricCiphertext
 *
 * @brief This data structure encapsulates a ciphertext generated with an
 * approved symmetric algorithm. 
 *
 * <br><br><b>Critical information fields</b>: If present, this is a critical
 * information field as defined in 5.2.6. An implementation that does not
 * recognize the indicated CHOICE value for this type in an encrypted SPDU
 * shall reject the SPDU as invalid.
 */
  SymmetricCiphertext ::= CHOICE { 
    aes128ccm  AesCcmCiphertext,
    ...
  }

/** 
 * @class AesCcmCiphertext
 *
 * @brief This data structure encapsulates an encrypted ciphertext for the
 * AES-CCM symmetric algorithm. It contains the following fields:
 *
 * <br><br>The ciphertext is 16 bytes longer than the corresponding plaintext.
 *
 * <br><br>The plaintext resulting from a correct decryption of the
 * ciphertext is a COER-encoded Ieee1609Dot2Data structure.
 *
 * @param nonce contains the nonce N as specified in 5.3.7. 
 *
 * @param ccmCiphertext contains the ciphertext C as specified in 5.3.7.
 */
  AesCcmCiphertext ::= SEQUENCE { 
    nonce          OCTET STRING (SIZE (12)),
	ccmCiphertext  Opaque 
  }

/** 
 * @class Countersignature
 *
 * @brief This data structure is used to perform a countersignature over an
 * already-signed SPDU. This is the profile of an Ieee1609Dot2Data containing
 * a signedData. The tbsData within content is composed of a payload
 * containing the hash (extDataHash) of the externally generated, pre-signed
 * SPDU over which the countersignature is performed.
 */
  Countersignature ::= Ieee1609Dot2Data (WITH COMPONENTS {...,
    content (WITH COMPONENTS {..., 
      signedData  (WITH COMPONENTS {..., 
        tbsData (WITH COMPONENTS {..., 
          payload (WITH COMPONENTS {..., 
            data ABSENT,
            extDataHash PRESENT
          }),
          headerInfo(WITH COMPONENTS {..., 
            generationTime PRESENT,
            expiryTime ABSENT,
            generationLocation ABSENT,
            p2pcdLearningRequest ABSENT,
            missingCrlIdentifier ABSENT,
            encryptionKey ABSENT
          })
        })
      })
    })
  })

--***************************************************************************--
--                Certificates and other Security Management                 --
--***************************************************************************--

/** 
 * @class Certificate
 *
 * @brief This structure is a profile of the structure CertificateBase which
 * specifies the valid combinations of fields to transmit implicit and
 * explicit certificates.
 */
  Certificate ::= CertificateBase (ImplicitCertificate | ExplicitCertificate)

/** 
 * @class SequenceOfCertificate
 *
 * @brief This type is used for clarity of definitions.
 */
  SequenceOfCertificate ::= SEQUENCE OF Certificate

/** 
 * @class CertificateBase
 *
 * @brief The fields in this structure have the following meaning:
 *
 * <br><br><b>Encoding considerations</b>: When a certificate is encoded for
 * hashing, for example to generate its HashedId8, or when it is to be used
 * as the <i>signer identifier information</i> for verification, it is
 * canonicalized as follows:
 * <ul>
 * <li> The encoding of toBeSigned uses the compressed form for all elliptic
 * curve points: that is, those points indicate a choice of compressed-y-0 or
 * compressed-y-1.</li>
 *
 * <li> The encoding of the signature, if present and if an ECDSA signature,
 * takes the r value to be an EccP256CurvePoint or EccP384CurvePoint
 * indicating the choice x-only.</li>
 * </ul>
 *
 * <br><br><b>Whole-certificate hash</b>: If the entirety of a certificate is
 * hashed to calculate a HashedId3, HashedId8, or HashedId10, the algorithm
 * used for this purpose is known as the <i>whole-certificate hash</i>.
 * <ul>
 * <li> The whole-certificate hash is SHA-256 if the certificate is an
 * implicit certificate.</li>
 *
 * <li> The whole-certificate hash is SHA-256 if the certificate is an
 * explicit certificate and toBeSigned.verifyKeyIndicator.verificationKey is
 * an EccP256CurvePoint.</li>
 *
 * <li> The whole-certificate hash is SHA-384 if the certificate is an
 * explicit certificate and toBeSigned.verifyKeyIndicator.verificationKey is
 * an EccP384CurvePoint.</li>
 * </ul>
 *
 * <b>Parameters</b>:
 *
 * @param version contains the version of the certificate format. In this
 * version of the data structures, this field is set to 3.
 *
 * @param type states whether the certificate is implicit or explicit. This
 * field is set to explicit for explicit certificates and to implicit for
 * implicit certificates. See ExplicitCertificate and ImplicitCertificate for
 * more details.
 *
 * @param issuer identifies the issuer of the certificate.
 *
 * @param toBeSigned is the certificate contents. This field is an input to
 * the hash when generating or verifying signatures for an explicit
 * certificate, or generating or verifying the public key from the
 * reconstruction value for an implicit certificate. The details of how this
 * field are encoded are given in the description of the
 * ToBeSignedCertificate type.
 *
 * @param signature is included in an ExplicitCertificate. It is the
 * signature, calculated by the signer identified in the issuer field, over
 * the hash of toBeSigned. The hash is calculated as specified in 5.3.1, where:
 * <ul>
 * <li> Data input is the encoding of toBeSigned following the COER.</li>
 *
 * <li> Signer identifier input depends on the verification type, which in
 * turn depends on the choice indicated by issuer. If the choice indicated by
 * issuer is self, the verification type is self-signed and the signer
 * identifier input is the empty string. If the choice indicated by issuer is
 * not self, the verification type is certificate and the signer identifier
 * input is the canonicalized COER encoding of the certificate indicated by
 * issuer. The canonicalization is carried out as specified in the <b>Encoding
 * consideration</b>s section of this subclause.</li>
 * </ul>
 */
  CertificateBase ::= SEQUENCE { 
    version     Uint8(3),
    type        CertificateType,
    issuer      IssuerIdentifier,
    toBeSigned  ToBeSignedCertificate,
    signature   Signature OPTIONAL
  }

/** 
 * @class CertificateType
 *
 * @brief This enumerated type indicates whether a certificate is explicit or
 * implicit.
 *
 * <br><br><b>Critical information fields</b>: If present, this is a critical
 * information field as defined in 5.2.5. An implementation that does not
 * recognize the indicated CHOICE for this type when verifying a signed SPDU
 * shall indicate that the signed SPDU is invalid.
 */  
  CertificateType ::= ENUMERATED {
    explicit,
    implicit,
    ...
  }

/** 
 * @class ImplicitCertificate
 *
 * @brief This is a profile of the CertificateBase structure providing all
 * the fields necessary for an implicit certificate, and no others.
 */
  ImplicitCertificate ::= CertificateBase (WITH COMPONENTS {...,
    type(implicit),
    toBeSigned(WITH COMPONENTS {..., 
      verifyKeyIndicator(WITH COMPONENTS {reconstructionValue})
    }), 
    signature ABSENT
  })

/** 
 * @class ExplicitCertificate
 *
 * @brief This is a profile of the CertificateBase structure providing all
 * the fields necessary for an explicit certificate, and no others.
 */
  ExplicitCertificate ::= CertificateBase (WITH COMPONENTS {...,
      type(explicit),
      toBeSigned(WITH COMPONENTS {..., 
          verifyKeyIndicator(WITH COMPONENTS {verificationKey})
      }), 
      signature PRESENT
  })

/** 
 * @class IssuerIdentifier
 *
 * @brief This structure allows the recipient of a certificate to determine
 * which keying material to use to authenticate the certificate. 
 *
 * <br><br>If the choice indicated is sha256AndDigest or sha384AndDigest:
 * <ul>
 * <li> The structure contains the HashedId8 of the issuing certificate,
 * where the certificate is canonicalized as specified in 6.4.3 before
 * hashing and the HashedId8 is calculated with the whole-certificate hash
 * algorithm, determined as described in 6.4.3.</li>
 *
 * <li> The hash algorithm to be used to generate the hash of the certificate
 * for verification is SHA-256 (in the case of sha256AndDigest) or SHA-384
 * (in the case of sha384AndDigest).</li>
 *
 * <li> The certificate is to be verified with the public key of the
 * indicated issuing certificate.</li>
 * </ul>
 *
 * If the choice indicated is self:
 * <ul>
 * <li> The structure indicates what hash algorithm is to be used to generate
 * the hash of the certificate for verification.</li>
 * 
 * <li> The certificate is to be verified with the public key indicated by
 * the verifyKeyIndicator field in theToBeSignedCertificate.</li>
 * </ul>
 *
 * <br><br><b>Critical information fields</b>: If present, this is a critical
 * information field as defined in 5.2.5. An implementation that does not
 * recognize the indicated CHOICE for this type when verifying a signed SPDU
 * shall indicate that the signed SPDU is invalid.
 */
  IssuerIdentifier ::= CHOICE  { 
    sha256AndDigest  HashedId8,
    self             HashAlgorithm,
    ...,
    sha384AndDigest  HashedId8
  }

/** 
 * @class ToBeSignedCertificate
 *
 * @brief The fields in the ToBeSignedCertificate structure have the
 * following meaning:
 * 
 * <br><br><b>Encoding considerations</b>: The encoding of toBeSigned which
 * is input to the hash uses the compressed form for all public keys and
 * reconstruction values that are elliptic curve points: that is, those
 * points indicate a choice of compressed-y-0 or compressed-y-1. The encoding
 * of the issuing certificate uses the compressed form for all public key and
 * reconstruction values and takes the r value of an ECDSA signature, which
 * in this standard is an ECC curve point, to be of type x-only.
 *
 * <br><br>For both implicit and explicit certificates, when the certificate
 * is hashed to create or recover the public key (in the case of an implicit
 * certificate) or to generate or verify the signature (in the case of an
 * explicit certificate), the hash is Hash (<i>Data input</i>) || Hash (<i>
 * Signer identifier input</i>), where:
 * <ul>
 * <li> <i>Data input</i> is the COER encoding of toBeSigned, canonicalized
 * as described above.</li>
 *
 * <li> <i>Signer identifier input</i> depends on the verification type,
 * which in turn depends on the choice indicated by issuer. If the choice
 * indicated by issuer is self, the verification type is self-signed and the
 * signer identifier input is the empty string. If the choice indicated by
 * issuer is not self, the verification type is certificate and the signer
 * identifier input is the COER encoding of the canonicalization per 6.4.3 of
 * the certificate indicated by issuer.</li>
 * </ul>
 *
 * In other words, for implicit certificates, the value H (CertU) in SEC 4,
 * section 3, is for purposes of this standard taken to be H [H
 * (canonicalized ToBeSignedCertificate from the subordinate certificate) ||
 * H (entirety of issuer Certificate)]. See 5.3.2 for further discussion,
 * including material differences between this standard and SEC 4 regarding
 * how the hash function output is converted from a bit string to an integer.
 *
 * <br><br>NOTE: This encoding of the implicit certificate for hashing has
 * been changed from the encoding specified in IEEE Std 1609.2-2013 for
 * consistency with the encoding of the explicit certificates. This
 * definition of the encoding results in implicit and explicit certificates
 * both being hashed as specified in 5.3.1.
 *
 * <br><br><b>Critical information fields</b>: 
 * <ul>
 * <li> If present, appPermissions is a critical information field as defined
 * in 5.2.6. An implementation that does not support the number of PsidSsp in
 * appPermissions shall reject the signed SPDU as invalid. A compliant
 * implementation shall support appPermissions fields containing at least
 * eight entries.</li>
 *
 * <li> If present, certIssuePermissions is a critical information field as
 * defined in 5.2.6. An implementation that does not support the number of
 * PsidGroupPermissions in certIssuePermissions shall reject the signed SPDU
 * as invalid. A compliant implementation shall support certIssuePermissions
 * fields containing at least eight entries.</li>
 *
 * <li> If present, certRequestPermissions is a critical information field as
 * defined in 5.2.6. An implementation that does not support the number of
 * PsidGroupPermissions in certRequestPermissions shall reject the signed
 * SPDU as invalid. A compliant implementation shall support
 * certRequestPermissions fields containing at least eight entries.</li>
 * </ul>
 *
 * <b>Parameters</b>:
 *
 * @param id contains information that is used to identify the certificate
 * holder if necessary.
 *
 * @param cracaId identifies the Certificate Revocation Authorization CA
 * (CRACA) responsible for certificate revocation lists (CRLs) on which this
 * certificate might appear. Use of the cracaId is specified in 5.1.3. The
 * HashedId3 is calculated with the whole-certificate hash algorithm,
 * determined as described in 6.4.12.
 *
 * @param crlSeries represents the CRL series relevant to a particular
 * Certificate Revocation Authorization CA (CRACA) on which the certificate
 * might appear. Use of this field is specified in 5.1.3. 
 *
 * @param validityPeriod contains the validity period of the certificate.
 *
 * @param region, if present, indicates the validity region of the
 * certificate. If it is omitted the validity region is indicated as follows:
 * <ul>
 * <li> If enclosing certificate is self-signed, i.e., the choice indicated
 * by the issuer field in the enclosing certificate structure is self, the
 * certificate is valid worldwide.</li>
 *
 * <li> Otherwise, the certificate has the same validity region as the
 * certificate that issued it.</li>
 * </ul>
 *
 * @param assuranceLevel indicates the assurance level of the certificate
 * holder.
 *
 * @param appPermissions indicates the permissions that the certificate
 * holder has to sign application data with this certificate. A valid
 * instance of appPermissions contains any particular Psid value in at most
 * one entry.  
 *
 * @param certIssuePermissions indicates the permissions that the certificate
 * holder has to sign certificates with this certificate. A valid instance of
 * this array contains no more than one entry whose psidSspRange field
 * indicates all. If the array has multiple entries and one entry has its
 * psidSspRange field indicate all, then the entry indicating all specifies
 * the permissions for all PSIDs other than the ones explicitly specified in
 * the other entries. See the description of PsidGroupPermissions for further
 * discussion.
 *
 * @param certRequestPermissions indicates the permissions that the
 * certificate holder has to sign certificate requests with this certificate.
 * A valid instance of this array contains no more than one entry whose
 * psidSspRange field indicates all. If the array has multiple entries and
 * one entry has its psidSspRange field indicate all, then the entry
 * indicating all specifies the permissions for all PSIDs other than the ones
 * explicitly specified in the other entries. See the description of
 * PsidGroupPermissions for further discussion.
 *
 * @param canRequestRollover indicates that the certificate may be used to
 * sign a request for another certificate with the same permissions. This
 * field is provided for future use and its use is not defined in this
 * version of this standard.
 *
 * @param encryptionKey contains a public key for encryption for which the
 * certificate holder holds the corresponding private key. 
 *
 * @param verifyKeyIndicator contains material that may be used to recover
 * the public key that may be used to verify data signed by this certificate. 
 */
  ToBeSignedCertificate ::= SEQUENCE { 
    id                      CertificateId,
    cracaId                 HashedId3,
    crlSeries               CrlSeries,
    validityPeriod          ValidityPeriod,
    region                  GeographicRegion OPTIONAL,
    assuranceLevel          SubjectAssurance OPTIONAL,
    appPermissions          SequenceOfPsidSsp OPTIONAL,
    certIssuePermissions    SequenceOfPsidGroupPermissions OPTIONAL,
    certRequestPermissions  SequenceOfPsidGroupPermissions OPTIONAL, 
    canRequestRollover      NULL OPTIONAL,
    encryptionKey           PublicEncryptionKey OPTIONAL,
    verifyKeyIndicator      VerificationKeyIndicator,
    ...,
    flags                  BIT STRING {cubk (0)} (SIZE (8)) OPTIONAL
  }
  (WITH COMPONENTS { ..., appPermissions PRESENT} |
   WITH COMPONENTS { ..., certIssuePermissions PRESENT} |
   WITH COMPONENTS { ..., certRequestPermissions PRESENT})

/** 
 * @class CertificateId
 *
 * @brief This structure contains information that is used to identify the
 * certificate holder if necessary.
 *
 * <br><br><b>Critical information fields</b>: 
 * <ul>
 * <li> If present, this is a critical information field as defined in 5.2.6.
 * An implementation that does not recognize the choice indicated in this
 * field shall reject a signed SPDU as invalid.</li>
 * </ul>
 *
 * <b>Parameters</b>:
 *
 * @param linkageData is used to identify the certificate for revocation
 * purposes in the case of certificates that appear on linked certificate
 * CRLs. See 5.1.3 and 7.3 for further discussion.
 *
 * @param name is used to identify the certificate holder in the case of
 * non-anonymous certificates. The contents of this field are a matter of
 * policy and should be human-readable.
 *
 * @param binaryId supports identifiers that are not human-readable.
 *
 * @param none indicates that the certificate does not include an identifier.
 */
  CertificateId ::= CHOICE {
    linkageData  LinkageData,
    name         Hostname,
    binaryId     OCTET STRING(SIZE(1..64)),
    none         NULL,
    ...
  }

/** 
 * @class LinkageData
 *
 * @brief This structure contains information that is matched against
 * information obtained from a linkage ID-based CRL to determine whether the
 * containing certificate has been revoked. See 5.1.3.4 and 7.3 for details
 * of use.
 */
  LinkageData ::= SEQUENCE { 
    iCert                IValue,
    linkage-value        LinkageValue, 
    group-linkage-value  GroupLinkageValue OPTIONAL
  }
  
/** 
 * @class EndEntityType
 *
 * @brief This type indicates which type of permissions may appear in
 * end-entity certificates the chain of whose permissions passes through the
 * PsidGroupPermissions field containing this value. If app is indicated, the
 * end-entity certificate may contain an appPermissions field. If enroll is
 * indicated, the end-entity certificate may contain a certRequestPermissions
 * field.   
 */
  EndEntityType ::= BIT STRING {
    app (0), 
    enroll (1) 
  } (SIZE (8)) (ALL EXCEPT {})

/** 
 * @class PsidGroupPermissions
 *
 * @brief This structure states the permissions that a certificate holder has
 * with respect to issuing and requesting certificates for a particular set
 * of PSIDs. In this structure:
 *
 * <br><br> For examples, see D.5.3 and D.5.4.
 *
 * @param subjectPermissions indicates PSIDs and SSP Ranges covered by this
 * field.
 *
 * @param minChainLength and chainLengthRange indicate how long the
 * certificate chain from this certificate to the end-entity certificate is
 * permitted to be. As specified in 5.1.2.1, the length of the certificate
 * chain is the number of certificates "below" this certificate in the chain,
 * down to and including the end-entity certificate. The length is permitted
 * to be (a) greater than or equal to minChainLength certificates and (b)
 * less than or equal to minChainLength + chainLengthRange certificates. A
 * value of 0 for minChainLength is not permitted when this type appears in
 * the certIssuePermissions field of a ToBeSignedCertificate; a certificate
 * that has a value of 0 for this field is invalid. The value â1 for
 * chainLengthRange is a special case: if the value of chainLengthRange is â1
 * it indicates that the certificate chain may be any length equal to or
 * greater than minChainLength. See the examples below for further discussion. 
 *
 * @param eeType takes one or more of the values app and enroll and indicates
 * the type of certificates or requests that this instance of
 * PsidGroupPermissions in the certificate is entitled to authorize. If this
 * field indicates app, the chain is allowed to end in an authorization
 * certificate, i.e., a certficate in which these permissions appear in an
 * appPermissions field (in other words, if the field does not indicate app
 * but the chain ends in an authorization certificate, the chain shall be
 * considered invalid). If this field indicates enroll, the chain is allowed
 * to end in an enrollment certificate, i.e., a certificate in which these
 * permissions appear in a certReqPermissions permissions field), or both (in
 * other words, if the field does not indicate app but the chain ends in an
 * authorization certificate, the chain shall be considered invalid).
 * Different instances of PsidGroupPermissions within a ToBeSignedCertificate
 * may have different values for eeType.
 */
  PsidGroupPermissions ::= SEQUENCE {
    subjectPermissions  SubjectPermissions,
    minChainLength      INTEGER DEFAULT 1, 
    chainLengthRange    INTEGER DEFAULT 0, 
    eeType              EndEntityType DEFAULT {app}
  }

/** 
 * @class SequenceOfPsidGroupPermissions
 *
 * @brief This type is used for clarity of definitions.
 */
  SequenceOfPsidGroupPermissions ::= SEQUENCE OF PsidGroupPermissions

/** 
 * @class SubjectPermissions
 *
 * @brief This indicates the PSIDs and associated SSPs for which certificate
 * issuance or request permissions are granted by a PsidGroupPermissions
 * structure. If this takes the value explicit, the enclosing
 * PsidGroupPermissions structure grants certificate issuance or request
 * permissions for the indicated PSIDs and SSP Ranges. If this takes the
 * value all, the enclosing PsidGroupPermissions structure grants certificate
 * issuance or request permissions for all PSIDs not indicated by other
 * PsidGroupPermissions in the same certIssuePermissions or
 * certRequestPermissions field.
 *
 * <br><br><b>Critical information fields</b>:
 * <ul>
 * <li> If present, this is a critical information field as defined in 5.2.6.
 * An implementation that does not recognize the indicated CHOICE when
 * verifying a signed SPDU shall indicate that the signed SPDU is
 * invalid.</li>
 *
 * <li> If present, explicit is a critical information field as defined in
 * 5.2.6. An implementation that does not support the number of PsidSspRange
 * in explicit when verifying a signed SPDU shall indicate that the signed
 * SPDU is invalid. A compliant implementation shall support explicit fields
 * containing at least eight entries.</li>
 * </ul>
 */
  SubjectPermissions ::= CHOICE {
          explicit        SequenceOfPsidSspRange,
          all             NULL,
          ...
  }

/** 
 * @class VerificationKeyIndicator
 *
 * @brief The contents of this field depend on whether the certificate is an
 * implicit or an explicit certificate.
 *
 * <br><br><b>Critical information fields</b>: If present, this is a critical
 * information field as defined in 5.2.5. An implementation that does not
 * recognize the indicated CHOICE for this type when verifying a signed SPDU
 * shall indicate that the signed SPDU is invalid.
 *
 * <br><br><b>Parameters</b>:
 *
 * @param verificationKey is included in explicit certificates. It contains
 * the public key to be used to verify signatures generated by the holder of
 * the Certificate.
 *
 * @param reconstructionValue is included in implicit certificates. It
 * contains the reconstruction value, which is used to recover the public key
 * as specified in SEC 4 and 5.3.2. 
 */
  VerificationKeyIndicator ::= CHOICE {
    verificationKey      PublicVerificationKey,
    reconstructionValue  EccP256CurvePoint,
    ...
  }
  
END

EtsiTs103097ExtensionModule
{itu-t(0) identified-organization(4) etsi(0) itsDomain(5) wg5(5) secHeaders(103097) extension(2) major-version-1(1) minor-version-1(1)} 
DEFINITIONS AUTOMATIC TAGS ::= BEGIN

IMPORTS 
  HashedId8,
  Time32
FROM Ieee1609Dot2BaseTypes {iso(1) identified-organization(3) ieee(111) 
    standards-association-numbered-series-standards(2) wave-stds(1609)  
    dot2(2) base(1) base-types(2) major-version-2 (2) minor-version-3 (3)}
/* WITH Successors */    
;

ExtensionModuleVersion::= INTEGER(1)

/* Extension {EXT-TYPE : ExtensionTypes} ::= SEQUENCE {
    id      EXT-TYPE.&extId({ExtensionTypes}),
    content EXT-TYPE.&ExtContent({ExtensionTypes}{@.id})
} */

Extension {EXT-TYPE : ExtensionTypes} ::= SEQUENCE {
    id      INTEGER,
    content INTEGER
}

/*EXT-TYPE ::= CLASS {
    &extId        ExtId,
    &ExtContent
} WITH SYNTAX {&ExtContent IDENTIFIED BY &extId} */

EXT-TYPE ::= SEQUENCE {
    extId        ExtId
}

ExtId ::= INTEGER(0..255)

EtsiOriginatingHeaderInfoExtension ::= Extension{{EtsiTs103097HeaderInfoExtensions}}

EtsiTs103097HeaderInfoExtensionId ::= ExtId
   etsiTs102941CrlRequestId      EtsiTs103097HeaderInfoExtensionId ::= 1 --'01'H
   etsiTs102941DeltaCtlRequestId EtsiTs103097HeaderInfoExtensionId ::= 2 --'02'H

EtsiTs103097HeaderInfoExtensions EXT-TYPE ::= {
   { EtsiTs102941CrlRequest       IDENTIFIED BY etsiTs102941CrlRequestId } |
   { EtsiTs102941DeltaCtlRequest  IDENTIFIED BY etsiTs102941DeltaCtlRequestId },
   ...
}

EtsiTs102941CrlRequest::= SEQUENCE {
    issuerId        HashedId8,
    lastKnownUpdate Time32 OPTIONAL
}

EtsiTs102941CtlRequest::= SEQUENCE {
    issuerId             HashedId8,
    lastKnownCtlSequence INTEGER (0..255) OPTIONAL
}

EtsiTs102941DeltaCtlRequest::= EtsiTs102941CtlRequest

END

EtsiTs103097Module
{itu-t(0) identified-organization(4) etsi(0) itsDomain(5) wg5(5) secHeaders(103097) core(1) major-version-3(3) minor-version-1(1)} 

DEFINITIONS AUTOMATIC TAGS ::= BEGIN

IMPORTS

Ieee1609Dot2Data, Certificate
FROM Ieee1609Dot2 {iso(1) identified-organization(3) ieee(111) 
  standards-association-numbered-series-standards(2) wave-stds(1609)  
  dot2(2) base(1) schema(1) major-version-2(2) minor-version-4(4)}
/* WITH Successors */

ExtensionModuleVersion
FROM EtsiTs103097ExtensionModule {itu-t(0) identified-organization(4)
  etsi(0) itsDomain(5) wg5(5) secHeaders(103097) extension(2) major-version-1(1) minor-version-1(1)}
;

EtsiTs103097Certificate::= Certificate (WITH COMPONENTS{...,
  toBeSigned (WITH COMPONENTS{...,
    id (WITH COMPONENTS{...,
      linkageData ABSENT,
      binaryId ABSENT
    }),
    certRequestPermissions ABSENT,
    canRequestRollover ABSENT
  })
}) 

EtsiTs103097Data::=Ieee1609Dot2Data (WITH COMPONENTS {..., 
  content (WITH COMPONENTS {...,
    signedData (WITH COMPONENTS {..., -- constraints on signed data headers
      tbsData (WITH COMPONENTS {              
        headerInfo (WITH COMPONENTS {...,
          generationTime PRESENT,
          p2pcdLearningRequest ABSENT,
          missingCrlIdentifier ABSENT
        })
      }),
      signer (WITH COMPONENTS {...,  --constraints on the certificate
        certificate ((WITH COMPONENT (EtsiTs103097Certificate))^(SIZE(1)))
      })
    }),
    encryptedData (WITH COMPONENTS {..., -- constraints on encrypted data headers
      recipients  (WITH COMPONENT (
        (WITH COMPONENTS {..., 
          pskRecipInfo ABSENT,
          symmRecipInfo ABSENT,
          rekRecipInfo ABSENT
        })
      ))
    }),
    signedCertificateRequest ABSENT
  })
})

EtsiTs103097Data-Unsecured {ToBeSentDataContent} ::= EtsiTs103097Data (WITH COMPONENTS {...,
  content (WITH COMPONENTS {
    unsecuredData (CONTAINING ToBeSentDataContent)
  })
})

EtsiTs103097Data-Signed {ToBeSignedDataContent} ::= EtsiTs103097Data (WITH COMPONENTS {..., 
  content (WITH COMPONENTS {
    signedData (WITH COMPONENTS {..., 
      tbsData (WITH COMPONENTS {
        payload (WITH COMPONENTS { 
          data (WITH COMPONENTS {...,
            content (WITH COMPONENTS {
              unsecuredData (CONTAINING ToBeSignedDataContent)
            })
          }) PRESENT
        })
      })
    })
  })
})

EtsiTs103097Data-SignedExternalPayload ::= EtsiTs103097Data (WITH COMPONENTS {..., 
  content (WITH COMPONENTS {
    signedData (WITH COMPONENTS {..., 
      tbsData (WITH COMPONENTS {
        payload (WITH COMPONENTS {
          extDataHash (WITH COMPONENTS {
            sha256HashedData PRESENT
          }) PRESENT
        })
      })
    })
  })
})

EtsiTs103097Data-Encrypted {ToBeEncryptedDataContent} ::= EtsiTs103097Data (WITH COMPONENTS {...,
  content (WITH COMPONENTS {
    encryptedData (WITH COMPONENTS {...,
      ciphertext (WITH COMPONENTS {...,
        aes128ccm (WITH COMPONENTS {...,
          ccmCiphertext (CONSTRAINED BY {-- ccm encryption of -- ToBeEncryptedDataContent}) 
        })
      })
    })
  })
})

EtsiTs103097Data-SignedAndEncrypted {ToBesignedAndEncryptedDataContent} ::= EtsiTs103097Data-Encrypted {EtsiTs103097Data-Signed {ToBesignedAndEncryptedDataContent}} 

EtsiTs103097Data-Encrypted-Unicast {ToBeEncryptedDataContent} ::= EtsiTs103097Data-Encrypted { EtsiTs103097Data-Unsecured{ToBeEncryptedDataContent}} (WITH COMPONENTS {...,
  content (WITH COMPONENTS {
    encryptedData (WITH COMPONENTS {...,
      recipients (SIZE(1))
    })
  })
})

EtsiTs103097Data-SignedAndEncrypted-Unicast {ToBesignedAndEncryptedDataContent} ::= EtsiTs103097Data-Encrypted {EtsiTs103097Data-Signed {ToBesignedAndEncryptedDataContent}} (WITH COMPONENTS {...,
  content (WITH COMPONENTS {
    encryptedData (WITH COMPONENTS {...,
      recipients (SIZE(1))
    })
  })
}) 

END

"""