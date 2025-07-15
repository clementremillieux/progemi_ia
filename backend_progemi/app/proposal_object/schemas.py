"""Proposal Object Schemas."""

from enum import Enum

from typing import List, Optional

from pydantic import BaseModel, Field


class TVA(str, Enum):
    """Représente une taxe sur la valeur ajoutée dans le devis."""

    TVA_20 = "TVA 20%"

    TVA_10 = "TVA 10%"

    TVA_5_5 = "TVA 5.5%"

    TVA_2_1 = "TVA 2.1%"

    TVA_0 = "TVA 0%"


class Produit(BaseModel):
    """Représente un produit dans le devis. Un produit peut avoir plusieurs sous-produits imbriqués."""

    label: str = Field(..., description="Label du produit")

    description: str = Field(..., description="Description du produit")

    quantite: float = Field(..., description="Quantité du produit")

    unitee_quantite: Optional[str] = Field(
        ...,
        description="Unité de la quantité du produit (ex: pièce, mètre, etc.)",
    )

    price_unitaire_ht: float = Field(
        ..., description="Prix unitaire hors taxe d'un produit"
    )

    tva: TVA = Field(..., description="Taxe sur la valeur ajoutée du sous-produit")

    eco_participation: Optional[float] = Field(
        ...,
        description="Montant de l'éco participation du produit",
    )

    sous_produits: Optional[List["Produit"]] = Field(
        ...,
        description="Liste des sous-produits du produit. Vide si le produit n'a pas de sous-produits.",
    )

    lot: str = Field(
        ...,
        description="Lot auquel appartient le produit",
    )


class Devis(BaseModel):
    """Le devis"""

    devis_total_ht: float = Field(..., description="Total hors taxe du devis")

    devis_total_ttc: float = Field(
        ..., description="Total toutes taxes comprises du devis"
    )

    devis_total_tva: float = Field(..., description="Total de la TVA du devis")

    devis_eco_participation: Optional[float] = Field(
        ...,
        description="Montant de l'éco participation du devis",
    )

    devis_produits: List[Produit] = Field(
        ...,
        description="Liste des produits du devis",
    )


class ProductWithPolygonAndValidation(Produit):
    """A product with an associated polygon and validation information."""

    polygon: List[float] = Field(
        ...,
        description="Polygon associated with the product for visualization (list of points)",
    )

    page: int = Field(
        ...,
        description="Page number associated with the polygon, if applicable",
    )

    issue: Optional[str] = Field(
        None,
        description="Issue or validation error associated with the product",
    )

    sous_produits: Optional[List["ProductWithPolygonAndValidation"]] = Field(
        default_factory=list,
        description="Nested sub-products with polygons/validation",
    )


class ProposalWithPolygonAndValidation(Devis):
    """A proposal with associated polygons and validation information."""

    issue_ht: Optional[str] = Field(
        None,
        description="Issue or validation error associated with the total HT",
    )

    issue_ttc: Optional[str] = Field(
        None, description="Issue or validation error associated with the total TTC"
    )

    issue_tva: Optional[str] = Field(
        None,
        description="Issue or validation error associated with the total TVA",
    )

    issue_additional_cost: Optional[str] = Field(
        None,
        description="Issue or validation error associated with the additional cost",
    )

    devis_produits: List[ProductWithPolygonAndValidation] = Field(
        ...,
        description="List of products in the proposal with associated polygons and validation information",
    )
